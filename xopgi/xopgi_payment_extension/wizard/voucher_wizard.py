# -*- coding: utf-8 -*-

from openerp import _, models, fields, api


class VoucherWizard(models.TransientModel):
    _name = "xopgi_payment_extension.voucher_wizard"

    def _default_journal(self):
        return self.env["account.journal"].search(
            [('type', 'in', ['bank', 'cash'])])[0]

    def _default_invoices(self):
        invoices = self.env["account.invoice"].browse(
            self._context.get("active_ids"))
        main_partner = invoices[0].partner_id
        main_type = invoices[0].type
        invoices = invoices & invoices.search(
            [("state", "=", "open"), ("partner_id", "=", main_partner.id),
             ("type", "=", main_type)])

        return invoices

    def _default_date(self):
        return fields.Date.context_today(self)

    @api.one
    @api.depends("invoice_ids")
    def _compute_invoice_dependencies(self):
        if any(self.invoice_ids):
            self.partner_id = self.invoice_ids[0].partner_id
            self.type = self.invoice_ids[0].type
            self.amount = sum(
                [invoice.residual for invoice in self.invoice_ids])
        else:
            self.partner_id = False
            self.type = False
            self.amount = 0.0

    type = fields.Char("Type", compute=_compute_invoice_dependencies)

    partner_id = fields.Many2one("res.partner", string="Partner",
                                 required=True, readonly=True,
                                 compute=_compute_invoice_dependencies)

    invoice_ids = fields.Many2many("account.invoice",
                                   string="Invoices", required=True,
                                   default=_default_invoices, readonly=True)

    amount = fields.Float("Amount", required=True,
                          compute=_compute_invoice_dependencies, readonly=True)

    journal_id = fields.Many2one("account.journal", string="Payment Method",
                                 required=True, default=_default_journal,
                                 domain=[('type', 'in', ['bank', 'cash'])])

    date = fields.Date('Date', default=_default_date,
                       help="Effective date for accounting entries")

    reference = fields.Char('Ref #', help="Transaction reference number.")

    @api.multi
    def quick_payment(self):
        context = {"partner_id": self.partner_id.id, "amount": self.amount,
                   "journal_id": self.journal_id.id, "date": self.date,
                   "reference": self.reference}
        if self.type == 'in_invoice':
            account_type = 'payable'
            context["type"] = 'payment'
        else:
            account_type = 'receivable'
            context["type"] = 'receipt'
        move_line_ids = []
        for invoice in self.invoice_ids:
            moves = self.env["account.move.line"].search(
                [("invoice", "=", invoice.id), ('state', '=', 'valid'),
                 ('account_id.type', '=', account_type),
                 ('reconcile_id', '=', False)])
            for move in moves:
                move_line_ids.append(move.id)
        context["move_line_ids"] = move_line_ids
        voucher = self.env["account.voucher"].with_context(context).new(
            context)
        voucher_change = voucher.onchange_partner_id(
            self.partner_id.id, self.journal_id.id, self.amount,
            voucher.currency_id, context["type"], self.date)
        line_dr_ids = voucher_change["value"]["line_dr_ids"]
        line_cr_ids = voucher_change["value"]["line_cr_ids"]
        del voucher_change["value"]["line_dr_ids"]
        del voucher_change["value"]["line_cr_ids"]
        voucher_change["value"]["partner_id"] = context["partner_id"]
        voucher_change["value"]["amount"] = context["amount"]
        voucher_change["value"]["journal_id"] = 5
        voucher_change["value"]["type"] = context["type"]
        voucher = self.env["account.voucher"].create(voucher_change["value"])
        for line_dr_id in line_dr_ids:
            line_dr_id["voucher_id"] = voucher.id
            self.env["account.voucher.line"].create(line_dr_id)
        for line_cr_id in line_cr_ids:
            line_cr_id["voucher_id"] = voucher.id
            self.env["account.voucher.line"].create(line_cr_id)
        voucher.proforma_voucher()
        return { }

    @api.multi
    def prepare_payment(self):
        action = {
            "type": "ir.actions.act_window",
            "res_model": "account.voucher",
            "context": {"partner_id": self.partner_id.id,
                        "amount": self.amount,
                        "journal_id": self.journal_id.id, "date": self.date,
                        "reference": self.reference}
        }
        if self.type == 'in_invoice':
            account_type = 'payable'
            action["context"]["type"] = 'payment'
            form_external_id = "account_voucher.view_vendor_payment_form"
        else:
            account_type = 'receivable'
            form_external_id = "account_voucher.view_vendor_receipt_form"
        line_dr_ids = []
        line_cr_ids = []
        for invoice in self.invoice_ids:
            moves = self.env["account.move.line"].search(
                [("invoice", "=", invoice.id), ('state', '=', 'valid'),
                 ('account_id.type', '=', account_type),
                 ('reconcile_id', '=', False)])
            for move in moves:
                if account_type == 'payable':
                    line_dr_ids.append(move.id)
                else:
                    line_cr_ids.append(move.id)

        action["views"] = [[self.env.ref(form_external_id).id, "form"]]
        action["context"]["line_dr_ids"] = line_dr_ids
        action["context"]["line_cr_ids"] = line_cr_ids
        return action
