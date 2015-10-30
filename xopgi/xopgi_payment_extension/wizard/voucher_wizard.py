#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# voucher_wizard
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise Autrement and Contributors
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


from openerp import models, fields, api


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

    type = fields.Char("Type", compute="_compute_invoice_dependencies")

    partner_id = fields.Many2one("res.partner", string="Partner",
                                 required=True, readonly=True,
                                 compute="_compute_invoice_dependencies")

    invoice_ids = fields.Many2many("account.invoice",
                                   string="Invoices", required=True,
                                   default=_default_invoices, readonly=True)

    move_line_ids = fields.Many2many("account.move.line",
                                     compute="_compute_invoice_dependencies")

    amount = fields.Float("Amount", readonly=True)

    journal_id = fields.Many2one("account.journal", string="Payment Method",
                                 required=True, default=_default_journal,
                                 domain=[('type', 'in', ['bank', 'cash'])])

    date = fields.Date('Date', default=_default_date,
                       help="Effective date for accounting entries")

    reference = fields.Char('Ref #', help="Transaction reference number.")

    @api.one
    @api.depends("invoice_ids")
    def _compute_invoice_dependencies(self):
        if any(self.invoice_ids):
            self.partner_id = self.invoice_ids[0].partner_id.id
            self.type = self.invoice_ids[0].type
            self.move_line_ids = self._get_move_lines()
        else:
            self.partner_id = False
            self.type = False

    @api.onchange("journal_id", "invoice_ids", "type")
    def _onchange_journal_or_invoice_or_type(self):
        voucher_lines = self._recompute_voucher_lines()
        self.amount = self._calculate_amount(voucher_lines)

    @api.multi
    def quick_payment(self):
        # For some reason self.amount change to 0.00 so is necessary
        # recalulate it. Keep searching for reason and solution :(
        voucher_lines = self._recompute_voucher_lines()
        amount = self._calculate_amount(voucher_lines)
        context = {"partner_id": self.partner_id.id, "amount": amount,
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
                        # For some reason self.amount change to 0.00 so is
                        # necessary recalulate it. Keep searching for reason
                        # and solution :(
                        "amount": self._calculate_amount(
                            self._recompute_voucher_lines()),
                        "journal_id": self.journal_id.id, "date": self.date,
                        "reference": self.reference,
                        "type": self._get_operation_type(),
                        "flag_reconcile": True}
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
                "move_line_ids": [move.id for move in self.move_line_ids]}
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
        return sum([line["amount_unreconciled"] for line in voucher_lines])
