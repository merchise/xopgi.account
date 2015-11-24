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

    primary_salesperson_id = fields.Many2one(
        "res.users", string="Salesperson",
        help="Primary salesperson in operation",
        compute="_compute_primary_salesperson", store=True)

    supplier_invoice_id = fields.Many2one('account.invoice',
                                          ondelete='set null')

    @api.depends('debit', 'balance')
    def _compute_commission(self):
        for record in self:
            # XXX: Technically debit != invoiced, since purchase refunds
            # increase debit.  Nevertheless we can't ignore that.
            invoiced, balance = record.debit, record.balance
            percentage = balance/invoiced if invoiced > 0 else 0  # 0 invoice -> 0%
            record.percentage_margin = percentage * 100
            # TODO: Change this to rules configurable from the UI.  Otherwise
            # this is not general enough to be at the xopgi level (xopgi means
            # applicable to every kind of enterprise, not just 'autrements'
            # much less CA itself).  Even CA may change it's method in the
            # future.
            if percentage >= 0.15:
                factor = percentage * 2
                if math.floor(factor) < 1:
                    if invoiced <= 4000:
                        factor += 0.2
                else:
                    factor = 1
                record.percentage_commission = factor * 5
            elif percentage < 0:
                # The commission of a very bad sale (where costs out-weighted
                # sales) remains the same.  This is mostly informative: how
                # much did the company lose with this sale?
                record.percentage_commission = -percentage
            else:
                record.percentage_commission = 0
            record.commission = record.percentage_commission * balance / 100

    @api.depends("type", "line_ids.invoice_id.user_id.name")
    def _compute_primary_salesperson(self):
        for record in self:
            if record.type != "contract":
                record.primary_salesperson_id = False
            else:
                main_line = record.line_ids.search(
                    [("account_id", "=", record.id),
                     ("invoice_id.user_id", "!=", False)], limit=1, order="id")
                if any(main_line):
                    record.primary_salesperson_id = main_line.invoice_id.user_id
                else:
                    record.primary_salesperson_id = False

    @api.one
    def has_many_salespeople(self):
        if self.type != "contract":
            return False
        else:
            lines = self.line_ids.search(
                [("account_id", "=", self.id),
                 ("invoice_id.user_id", "!=", False)])
            if any(lines):
                salesperson = lines[0].invoice_id.user_id
                for line in lines[1:]:
                    if line.invoice_id.user_id != salesperson:
                        return True
                return False
            return False
