# -*- coding: utf-8 -*-


import math
from openerp import api, fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    percentage_margin = fields.Float(
        string='Margin %', help='Percentage margin related to credit.',
        compute='_compute_commission')

    percentage_commission = fields.Float(
        string='Commission %', help='Percentage commission related to profit.',
        compute='_compute_commission')

    commission = fields.Float(
        string='Commission', help='Commission related to profit.',
        compute='_compute_commission')

    @api.one
    @api.depends('debit', 'balance')
    def _compute_commission(self):
        if self.balance == 0:
            self.percentage_margin = 0
        else:
            self.percentage_margin = self.balance / self.debit * 100

        percentage_abs = math.fabs(self.percentage_margin / 100.0)

        if percentage_abs >= 0.15:
            factor = percentage_abs / 0.5
            if math.floor(factor) < 1:
                if self.debit <= 4000:
                    factor += 0.2
            else:
                factor = 1
            self.percentage_commission = factor * 5
        else:
            self.percentage_commission = 0

        self.commission = self.percentage_commission * self.balance / 100
