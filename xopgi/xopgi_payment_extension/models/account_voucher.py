# -*- coding: utf-8 -*-

from openerp import models


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    def recompute_voucher_lines(self, cr, uid, ids, partner_id, journal_id,
                                price, currency_id, ttype, date, context=None):
        result = super(AccountVoucher, self).recompute_voucher_lines(
            cr, uid,
            ids, partner_id, journal_id, price,
            currency_id, ttype, date, context=context)

        if "line_dr_ids" in context and any(context["line_dr_ids"]):
            context_line_dr_ids = context["line_dr_ids"]
            for line_dr_id in result["value"]["line_dr_ids"][:]:
                if line_dr_id["move_line_id"] not in context_line_dr_ids:
                    result["value"]["line_dr_ids"].remove(line_dr_id)
                elif "from_wizard" in context and context["from_wizard"]:
                    line_dr_id["amount"] = line_dr_id["amount_unreconciled"]
                    line_dr_id["reconcile"] = True

        if "line_cr_ids" in context and any(context["line_cr_ids"]):
            context_line_cr_ids = context["line_cr_ids"]
            for line_cr_id in result["value"]["line_cr_ids"][:]:
                if line_cr_id["move_line_id"] not in context_line_cr_ids:
                    result["value"]["line_cr_ids"].remove(line_cr_id)
                elif "from_wizard" in context and context["from_wizard"]:
                    line_cr_id["amount"] = line_cr_id["amount_unreconciled"]
                    line_cr_id["reconcile"] = True

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
