# -*- coding: utf-8 -*-

import datetime
from openerp import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    to_be_reversed = fields.Boolean(
        'To Be Reversed', readonly=True,
        help='True if entry has to be reversed at the end of period.')

    move_reversal_id = fields.Many2one('account.move', string='Reversal Entry',
                                       ondelete='set null', readonly=True)

    @api.one
    def reverse_and_reconcile_move(self, date):
        period = self.env["account.period"].get_period_by_date(date)

        reverse_move = self.copy(
            {"period_id": period.id, "date": date, "move_reversal_id": self.id,
             "name": "REV " + self.name, "to_be_reversed": False})
        for line in reverse_move.line_id:
            reconcile = self.env["account.move.reconcile"].create(
                {"opening_reconciliation": False, "type": "manual"})
            credit = line.credit
            debit = line.debit
            line.write({"credit": debit, "debit": credit, "date": date,
                        "reconcile_ref": reconcile.name,
                        "reconcile_id": reconcile.id})

            line_to_reconcile = self.line_id.search(
                [("move_id", "=", self.id),
                 ("account_id", "=", line.account_id.id),
                 ("debit", "=", line.credit), ("credit", "=", line.debit),
                 ("reconcile_id", "=", False)], limit=1)
            line_to_reconcile.write({"reconcile_ref": reconcile.name,
                                     "reconcile_id": reconcile.id})

        self.write(
            {"to_be_reversed": False, "move_reversal_id": reverse_move.id})

        return reverse_move;


class AccountPeriod(models.Model):
    _inherit = "account.period"

    def get_period_by_date(self, date):
        # Work around to avoid bug on opening period
        last_period_date = (datetime.date(
            datetime.MINYEAR + 1, date.month % 12 + 1, 1) - datetime.timedelta(
            days=2)).replace(year=date.year)
        return self.search([("date_stop", ">", last_period_date), (
            "date_start", "<", last_period_date)], limit=1)
