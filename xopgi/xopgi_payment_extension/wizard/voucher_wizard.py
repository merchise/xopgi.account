#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# voucher_wizard
# ---------------------------------------------------------------------
# Copyright (c) 2015, 2016 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-10-30


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)
import datetime
from openerp import models, fields, api


class VoucherWizard(models.TransientModel):
    _name = "xopgi_payment_extension.voucher_wizard"

    def _default_journal(self):
        return self.env["account.journal"].search(
            [('type', 'in', ['bank', 'cash'])])[0]

    def _default_invoices(self):
        invoices = self.env["account.invoice"].browse(
            self._context.get("active_ids"))
        main_partner = self._get_real_partner(invoices[0].partner_id)
        main_type = invoices[0].type
        invoices = invoices & invoices.search(
            [("state", "=", "open"), ("type", "=", main_type),
             "|", ("partner_id", "=", main_partner.id),
             ("partner_id.parent_id.id", "=", main_partner.id)])
        return invoices

    def _default_date(self):
        return fields.Date.context_today(self)

    type = fields.Char("Type", compute="_compute_invoice_dependencies")
    partner_id = fields.Many2one("res.partner", string="Partner",
                                 required=True, readonly=True,
                                 compute="_compute_invoice_dependencies")
    invoice_ids = fields.Many2many("account.invoice",
                                   string="Invoices", required=True,
                                   default=_default_invoices, readonly=True)
    move_line_ids = fields.Many2many("account.move.line",
                                     compute="_compute_invoice_dependencies")
    amount = fields.Float("Amount", required=True, readonly=True,
                          compute="_compute_amount")
    journal_id = fields.Many2one("account.journal", string="Payment Method",
                                 required=True, default=_default_journal,
                                 domain=[('type', 'in', ['bank', 'cash'])])
    date = fields.Date('Date', default=_default_date,
                       help="Effective date for accounting entries")
    reference = fields.Char('Ref #', help="Transaction reference number.")
    name = fields.Char('Memo')

    @api.depends("invoice_ids")
    def _compute_invoice_dependencies(self):
        for record in self:
            if any(self.invoice_ids):
                record.partner_id = record._get_real_partner(
                    record.invoice_ids[0].partner_id).id
                record.type = self.invoice_ids[0].type
                record.move_line_ids = self._get_move_lines()
            else:
                record.partner_id = False
                record.type = False

    @api.depends("journal_id", "move_line_ids", "type", "date")
    def _compute_amount(self):
        for record in self:
            voucher_lines = record._recompute_voucher_lines()
            record.amount = record._calculate_amount(voucher_lines)

    @api.multi
    def quick_payment(self):
        voucher_lines = self._recompute_voucher_lines()
        context = {"partner_id": self.partner_id.id, "amount": self.amount,
                   "journal_id": self.journal_id.id, "date": self.date,
                   "reference": self.reference,
                   "type": self._get_operation_type(),
                   "move_line_ids": [move.id for move in self.move_line_ids]}
        voucher = self.env["account.voucher"].with_context(context).new(
            context)
        voucher_change = voucher.onchange_partner_id(
            self.partner_id.id, self.journal_id.id, self.amount,
            self._get_currency(), context["type"], self.date)
        del voucher_change["value"]["line_dr_ids"]
        del voucher_change["value"]["line_cr_ids"]
        voucher_change["value"]["partner_id"] = context["partner_id"]
        voucher_change["value"]["amount"] = context["amount"]
        voucher_change["value"]["journal_id"] = context["journal_id"]
        voucher_change["value"]["type"] = context["type"]
        voucher_change["value"]["date"] = self.date
        voucher_change["value"]["period_id"] = self._get_period()
        voucher_change["value"]["reference"] = self.reference
        voucher_change["value"]["name"] = self.name
        voucher = self.env["account.voucher"].create(voucher_change["value"])
        if self.type == 'in_invoice':
            for line_dr_id in voucher_lines:
                line_dr_id["amount"] = line_dr_id["amount_unreconciled"]
                line_dr_id["reconcile"] = True
                line_dr_id["voucher_id"] = voucher.id
                self.env["account.voucher.line"].create(line_dr_id)
        else:
            for line_cr_id in voucher_lines:
                line_cr_id["amount"] = line_cr_id["amount_unreconciled"]
                line_cr_id["reconcile"] = True
                line_cr_id["voucher_id"] = voucher.id
                self.env["account.voucher.line"].create(line_cr_id)
        voucher.proforma_voucher()
        return {}

    @api.multi
    def prepare_payment(self):
        action = {
            "type": "ir.actions.act_window",
            "res_model": "account.voucher",
            "context": {"partner_id": self.partner_id.id,
                        "amount": self.amount,
                        "journal_id": self.journal_id.id, "date": self.date,
                        "reference": self.reference,
                        "type": self._get_operation_type(),
                        "period_id": self._get_period(),
                        "name": self.name,
                        "from_wizard": True}
        }
        if self.type == 'in_invoice':
            form_external_id = "account_voucher.view_vendor_payment_form"
            action["context"]["line_dr_ids"] = [move.id for move in
                                                self.move_line_ids]
        else:
            form_external_id = "account_voucher.view_vendor_receipt_form"
            action["context"]["line_cr_ids"] = [move.id for move in
                                                self.move_line_ids]
        action["views"] = [[self.env.ref(form_external_id).id, "form"]]
        return action

    def _get_move_lines(self):
        if not any(self.invoice_ids):
            return False

        move_line_ids = set()
        account_type = self._get_account_type()
        for invoice in self.invoice_ids:
            moves = self.env["account.move.line"].search(
                [("invoice", "=", invoice.id), ('state', '=', 'valid'),
                 ('account_id.type', '=', account_type),
                 ('reconcile_id', '=', False)])
            if any(move_line_ids):
                move_line_ids = move_line_ids | moves
            else:
                move_line_ids = moves
        return move_line_ids

    def _recompute_voucher_lines(self):
        if any(self.invoice_ids):
            currency_id = self._get_currency()
            voucher_data = {"journal_id": self.journal_id.id}
            context = {
                "move_line_ids": [move.id for move in self.move_line_ids],
                "date": self.date
            }
            voucher = self.env["account.voucher"].with_context(context).new(
                voucher_data)
            voucher_lines = voucher.recompute_voucher_lines(
                self.partner_id.id, self.journal_id.id, self.amount,
                currency_id, self._get_operation_type(), self.date)
            if self.type == 'in_invoice':
                return voucher_lines["value"]["line_dr_ids"]
            if self.type == 'out_invoice':
                return voucher_lines["value"]["line_cr_ids"]
        return False

    def _get_operation_type(self):
        if self.type == 'in_invoice':
            return "payment"
        return "receipt"

    def _get_account_type(self):
        if self.type == 'in_invoice':
            return "payable"
        return "receivable"

    def _get_currency(self):
        if self.journal_id.currency:
            return self.journal_id.currency.id
        return self.journal_id.company_id.currency_id.id

    def _calculate_amount(self, voucher_lines):
        if not voucher_lines:
            return 0.0
        return sum([line["amount_unreconciled"] for line in voucher_lines])

    def _get_period(self):
        # Work around to avoid bug on opening period
        date = fields.Date.from_string(self.date)
        last_period_date = (datetime.date(
            datetime.MINYEAR + 1, date.month % 12 + 1, 1) - datetime.timedelta(
            days=2)).replace(year=date.year)

        return self.env["account.period"].search(
            [("date_stop", ">", last_period_date), (
                "date_start", "<", last_period_date)], limit=1).id

    def _get_real_partner(self, basePartner):
        if not basePartner.is_company and any(basePartner.parent_id):
            return basePartner.parent_id
        return basePartner
