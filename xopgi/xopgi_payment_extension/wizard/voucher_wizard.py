# -*- coding: utf-8 -*-

from openerp import models, fields, api


class VoucherWizard(models.TransientModel):
    _name = "xopgi_payment_extension.voucher_wizard"

    def _default_invoices(self):
        invoices = self.env["account.invoice"].browse(
            self._context.get("active_ids"))
        main_partner = invoices[0].partner_id
        main_type = invoices[0].type
        invoices = invoices & invoices.search(
            [("state", "=", "open"), ("partner_id", "=", main_partner.id),
             ("type", "=", main_type)])

        return invoices

    @api.one
    @api.depends("invoice_ids")
    def _compute_partner_id(self):
        if any(self.invoice_ids):
            self.partner_id = self.invoice_ids[0].partner_id
            self.type = self.invoice_ids[0].type
        else:
            self.partner_id = False
            self.type = False

    type = fields.Char("Type", compute=_compute_partner_id)

    partner_id = fields.Many2one("res.partner", string="Partner",
                                 required=True, readonly=True,
                                 compute=_compute_partner_id)

    invoice_ids = fields.Many2many("account.invoice",
                                   string="Invoices", required=True,
                                   default=_default_invoices, readonly=True)

    @api.multi
    def prepare_payment(self):
        moves_ids = []
        account_type = False
        form_external_id = False
        if self.type == 'in_invoice':
            account_type = 'payable'
            form_external_id = "account_voucher.view_vendor_payment_form"
        else:
            account_type = 'receivable'
            form_external_id = "account_voucher.view_vendor_receipt_form"

        for invoice in self.invoice_ids:
            moves = self.env["account.move.line"].search(
                [("invoice", "=", invoice.id), ('state', '=', 'valid'),
                 ('account_id.type', '=', account_type),
                 ('reconcile_id', '=', False)])
            for move in moves:
                moves_ids.append(move.id)
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.voucher",
            "views": [[self.env.ref(form_external_id).id, "form"]],
            "context": {"partner_id": self.partner_id.id,
                        "move_line_ids": moves_ids}
        }
