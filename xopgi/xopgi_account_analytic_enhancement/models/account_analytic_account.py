# -*- coding: utf-8 -*-


from openerp import api, fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    percentage_margin = fields.Float(
        string='Margin %', help='Percentage margin related to credit.',
        compute='_compute_percentage_margin')

    @api.one
    @api.depends('debit', 'credit')
    def _compute_percentage_margin(self):
        if self.credit == 0:
            if self.debit == 0:
                self.percentage_margin = 0
            else:
                self.percentage_margin = 100
        else:
            self.percentage_margin = self.debit * 100 / self.credit - 100
            if self.percentage_margin > 100:
                self.percentage_margin = 100
