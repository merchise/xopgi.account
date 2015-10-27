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

        if "line_cr_ids" in context and any(context["line_cr_ids"]):
            context_line_cr_ids = context["line_cr_ids"]
            for line_cr_id in result["value"]["line_cr_ids"][:]:
                if line_cr_id["move_line_id"] not in context_line_cr_ids:
                    result["value"]["line_cr_ids"].remove(line_cr_id)

        return result
