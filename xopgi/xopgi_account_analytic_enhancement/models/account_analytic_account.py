# -*- coding: utf-8 -*-


from openerp import api, fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    percentage_profit = fields.Float(
        string='% Profit', help='Percentage profit account balance.',
        compute='_compute_percentage_profit')

    @api.one
    @api.depends('debit', 'credit')
    def _compute_percentage_profit(self):
        if self.credit == 0:
            if self.debit == 0:
                self.percentage_profit = 0;
            else:
                self.percentage_profit = 100;
        else:
            self.percentage_profit = self.debit * 100 / self.credit - 100
            if self.percentage_profit > 100:
                self.percentage_profit = 100