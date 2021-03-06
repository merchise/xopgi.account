#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
'''Extensions & fixes for account move lines.

'''
from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _absolute_import)

from xoeuf import fields, models, api


class MoveLine(models.Model):
    _inherit = 'account.move.line'

    # Trick to remove every attempt of the code to set the currency_id with
    # the same as the company's; which creates all sorts of problems.
    @api.constrains('currency_id')
    def _sanity_of_currency_id(self):
        for record in self:
            company_id = record.move_id.company_id
            currency_id = record.currency_id
            if currency_id and currency_id == company_id.currency_id:
                record.currency_id = None

    @api.multi
    @api.depends('line_currency_amount')
    def _get_currency_credit_debit(self):
        for line in self:
            company_id = line.move_id.company_id
            if line.currency_id and company_id.currency_id != line.currency_id:
                amount = line.line_currency_amount
                if amount > 0:
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
        company_id = self[0].move_id.company_id
        for line in self:
            if line.currency_id and company_id.currency_id != line.currency_id:
                line.line_currency_amount = line.amount_currency
            else:
                line.line_currency_amount = line.debit - line.credit

    @api.onchange('currency_debit', 'currency_credit', 'currency_id',
                  'company_id')
    def _adjust_debit_credit(self):
        self.line_currency_amount = self.currency_debit - self.currency_credit
        self._set_line_currency_amount()  # I have to trigger this by hand!

    @api.multi
    def _set_line_currency_amount(self):
        # It's best to go all the way to the move_id, since NewId records may
        # not have the company_id set.  This allows the _adjust_debit_credit
        # on-change method to use this method to compute the adjusted
        # debit/credit.
        company_id = self[0].move_id.company_id
        for line in self:
            amount = self.line_currency_amount
            if line.currency_id and company_id.currency_id != line.currency_id:
                line.amount_currency = amount
                line_currency = line.currency_id.with_context(
                    date=line.move_id.date
                )
                posted = line_currency.compute(
                    abs(amount),
                    company_id.currency_id,
                )
            else:
                line.currency_id = False
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
        company_id = self[0].move_id.company_id
        for line in self:
            if line.currency_id and company_id.currency_id != line.currency_id:
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
