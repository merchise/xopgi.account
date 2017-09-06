#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# account_voucher.py
# ---------------------------------------------------------------------
# Copyright (c) 2015-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)
from xoeuf import models


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    def recompute_voucher_lines(self, cr, uid, ids, partner_id, journal_id,
                                price, currency_id, ttype, date, context=None):
        result = super(AccountVoucher, self).recompute_voucher_lines(
            cr, uid,
            ids, partner_id, journal_id, price,
            currency_id, ttype, date, context=context)
        if any(context.get("line_dr_ids", [])):
            context_line_dr_ids = context["line_dr_ids"]
            for line_dr_id in result["value"]["line_dr_ids"][:]:
                # When lines are manually added to the voucher, line_dr_id came
                # in form of tuple, so is necessary to check
                if isinstance(line_dr_id, dict):
                    if line_dr_id["move_line_id"] not in context_line_dr_ids:
                        result["value"]["line_dr_ids"].remove(line_dr_id)
                    elif "from_wizard" in context and context["from_wizard"]:
                        line_dr_id["amount"] = line_dr_id[
                            "amount_unreconciled"]
                        line_dr_id["reconcile"] = True
        if any(context.get("line_cr_ids", [])):
            context_line_cr_ids = context["line_cr_ids"]
            for line_cr_id in result["value"]["line_cr_ids"][:]:
                # When lines are manually added to the voucher, line_cr_id came
                # in form of tuple, so is necessary to check
                if isinstance(line_cr_id, dict):
                    if line_cr_id["move_line_id"] not in context_line_cr_ids:
                        result["value"]["line_cr_ids"].remove(line_cr_id)
                    elif "from_wizard" in context and context["from_wizard"]:
                        line_cr_id["amount"] = line_cr_id[
                            "amount_unreconciled"]
                        line_cr_id["reconcile"] = True
        if context.get("from_wizard", None):
            result['value']['writeoff_amount'] = self._compute_writeoff_amount(
                cr, uid, result['value']['line_dr_ids'],
                result['value']['line_cr_ids'], price, ttype)

        return result

    def mark_all_credits(self, cr, uid, ids, context):
        current_voucher = self.browse(cr, uid, ids)
        for line_cr_id in current_voucher.line_cr_ids:
            line_cr_id.amount = line_cr_id.amount_unreconciled
            line_cr_id.reconcile = True

    def unmark_all_credits(self, cr, uid, ids, context):
        current_voucher = self.browse(cr, uid, ids)
        for line_cr_id in current_voucher.line_cr_ids:
            line_cr_id.amount = 0.00
            line_cr_id.reconcile = False

    def mark_all_debits(self, cr, uid, ids, context):
        current_voucher = self.browse(cr, uid, ids)
        for line_dr_id in current_voucher.line_dr_ids:
            line_dr_id.amount = line_dr_id.amount_unreconciled
            line_dr_id.reconcile = True

    def unmark_all_debits(self, cr, uid, ids, context):
        current_voucher = self.browse(cr, uid, ids)
        for line_dr_id in current_voucher.line_dr_ids:
            line_dr_id.amount = 0.00
            line_dr_id.reconcile = False

    def proforma_voucher(self, cr, uid, ids, context=None):
        current_vouchers = self.browse(cr, uid, ids)
        for current_voucher in current_vouchers:
            write_values = {}
            for line_cr_id in current_voucher.line_cr_ids:
                if line_cr_id.amount == 0.00:
                    write_values.setdefault(
                        "line_cr_ids", []).append((2, line_cr_id.id, 0))
            for line_dr_id in current_voucher.line_dr_ids:
                if line_dr_id.amount == 0.00:
                    write_values.setdefault(
                        "line_dr_ids", []).append((2, line_dr_id.id, 0))
            if any(write_values):
                current_voucher.write(write_values)
        return super(AccountVoucher, self).proforma_voucher(
            cr, uid, ids, context)
