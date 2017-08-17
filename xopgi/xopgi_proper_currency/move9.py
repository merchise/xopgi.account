# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi.xopgi.xopgi_account.move9
# ---------------------------------------------------------------------
# Copyright (c) 2013-2017 Merchise Autrement [~º/~]
# All rights reserved.
#
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#

'''Extensions & fixes for account move lines.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _absolute_import)

from xoeuf import fields, models, api

from xoeuf.models import get_modelname
from xoeuf.models.proxy import AccountMoveLine as BaseMoveLine


class MoveLine(models.Model):
    _inherit = this = get_modelname(BaseMoveLine)

    @api.multi
    @api.depends('line_currency_amount')
    def _get_currency_credit_debit(self):
        '''Functional getter for `credit` and `debit` fields.

        This changes the normal behaviour of a single :class:`journal item
        <account_move_line>`: Instead of having a separate `amount_currency`
        field when the currency is not the same as the one defined for
        company, use debit for positive `amount_currency` and credit for
        negative.

        '''
        for line in self:
            if line.currency_id:
                amount = line.line_currency_amount
                if  amount > 0:
                    line.currency_debit = amount
                    line.currency_credit = 0
                else:
                    line.currency_debit = 0
                    line.currency_credit = -amount
            else:
                line.currency_credit = line.credit
                line.currency_debit = line.debit

    @api.multi
    def _set_currency_credit_debit(self):
        for l in self:
            # This will trigger the _set_line_currency_amount below, which
            # does the calculation of debit and credit.
            l.line_currency_amount = l.currency_debit - l.currency_credit

    @api.multi
    @api.depends('amount_currency', 'debit', 'credit', 'currency_id')
    def _get_line_currency_amount(self):
        for line in self:
            if line.currency_id:
                line.line_currency_amount = line.amount_currency
            else:
                line.line_currency_amount = line.debit - line.credit

    @api.onchange('currency_debit', 'currency_credit', 'currency_id',
                  'company_id')
    def _adjust_debit_credit(self):
        self.line_currency_amount = self.currency_debit - self.currency_credit
        self._set_line_currency_amount()  # I have to trigger this by hand!
        return {
            'values': {
                'debit': self.debit,
                'credit': self.credit
            }
        }

    @api.multi
    def _set_line_currency_amount(self):
        # It's best to got all the way to the move_id, since NewId records may
        # not have the company_id set.  This allows the _adjust_debit_credit
        # on-change method to use this method to compute the adjusted
        # debit/credit.
        company_id = self[0].move_id.company_id
        for line in self:
            amount = self.line_currency_amount
            if line.currency_id:
                line.amount_currency = amount
                line_currency = line.currency_id.with_context(
                    date=line.move_id.date
                )
                posted = line_currency.compute(
                    abs(amount),
                    company_id.currency_id,
                )
            else:
                line.amount_currency = False
                posted = abs(amount)
            if amount > 0:
                line.debit = posted
                line.credit = 0
            else:
                line.debit = 0
                line.credit = posted

    @api.multi
    @api.depends('currency_id', 'company_id.currency_id')
    def _get_line_currency(self):
        for line in self:
            if line.currency_id:
                line.line_currency = line.currency_id
            else:
                line.line_currency = line.company_id.currency_id.id

    currency_debit = fields.Monetary(
        compute='_get_currency_credit_debit',
        inverse='_set_currency_credit_debit',
        store=True,
        string='Debit',
        currency_field='currency_id',
    )
    currency_credit = fields.Monetary(
        compute='_get_currency_credit_debit',
        inverse='_set_currency_credit_debit',
        store=True,
        string='Credit',
        currency_field='currency_id',
    )
    line_currency_amount = fields.Monetary(
        compute='_get_line_currency_amount',
        inverse='_set_line_currency_amount',
        store=True,
        string='Currency Amount',
        currency_field='currency_id',
    )
    line_currency = fields.Many2one(
        'res.currency',
        compute='_get_line_currency',
        store=True,
        string='Proper currency'
    )
