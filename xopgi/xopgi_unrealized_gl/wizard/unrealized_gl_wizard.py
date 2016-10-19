#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# unrealized_gl_wizard
# ---------------------------------------------------------------------
# Copyright (c) 2015-2016 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.

'''Perform the Unrealized Gain/Loss adjustment.



'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from openerp import api, fields, models

from xoeuf.osv.model_extensions import get_creator
from xoeuf.osv.orm import UNLINKALL_RELATED, CREATE_RELATED

from xoeuf.models import (
    AccountPeriod as Period,
    AccountMove as Move,
    AccountAccount as Account,
    ResCurrency as Currency,
    DecimalPrecision,
)


def _get_valid_accounts(currency=None):
    if currency is None:
        return Account.search(
            [("currency_id", "!=", False),
             ("type", "!=", "view")]
        )
    else:
        return Account.search(
            [("currency_id", "=", currency.id),
             ("type", "!=", "view")]
        )


class UnrealizedGLWizard(models.TransientModel):
    _name = "xopgi.unrealized_gl_wizard"

    def _get_valid_currencies(self):
        accounts = _get_valid_accounts()
        currencies = {account.currency_id.id for account in accounts}
        return [("id", "in", list(currencies))]

    def _get_currency(self):
        return Currency.search(self._get_valid_currencies(), limit=1)

    def _get_journal(self):
        return self.env.user.company_id.ugl_journal_id

    def _get_gain_account(self):
        return self.env.user.company_id.ugl_gain_account_id

    def _get_loss_account(self):
        return self.env.user.company_id.ugl_loss_account_id

    def _get_default_adjustments(self):
        currency = self._get_currency()
        accounts = _get_valid_accounts(currency)
        adjustments = []
        for account in accounts:
            with get_creator(self.env['xopgi.unrealized_gl_adjustment']) as c:
                c.update(account=account.id, wizard=self.id)
            adjustments.append(c.result)
        return adjustments

    close_date = fields.Date(
        string="Close Date",
        required=True,
        default=fields.Date.today
    )

    currency_id = fields.Many2one(
        "res.currency",
        "Currency",
        required=True,
        default=_get_currency,
        domain=_get_valid_currencies
    )

    currency_rate = fields.Float(
        string="Currency Rate",
        readonly=True,
        digits=(15, 9),
        compute='_compute_all'
    )

    journal_id = fields.Many2one(
        "account.journal",
        string="Journal",
        required=True,
        domain=[('type', '=', 'general')],
        default=_get_journal,
        readonly=True
    )

    gain_account_id = fields.Many2one(
        "account.account",
        string="Gain Account",
        required=True,
        domain=[('type', '=', 'other')],
        default=_get_gain_account,
        readonly=True
    )

    loss_account_id = fields.Many2one(
        "account.account",
        string="Loss Account",
        required=True,
        domain=[('type', '=', 'other')],
        default=_get_loss_account,
        readonly=True
    )

    adjustments = fields.One2many(
        'xopgi.unrealized_gl_adjustment',
        'wizard',
        compute='_compute_all',
    )

    @api.depends('close_date', 'currency_id')
    def _compute_all(self):
        company_currency = self.env.user.company_id.currency_id
        for record in self:
            if any(record.currency_id):
                record.currency_rate = self.currency_id.with_context(date=self.close_date).compute(
                    1,
                    company_currency,
                    round=False,
                )
                accounts = _get_valid_accounts(record.currency_id)
                adjustments = [
                    CREATE_RELATED(account=account, wizard=self)
                    for account in accounts
                ]
                record.adjustments = adjustments

    @api.multi
    def generate(self):
        self.ensure_one()
        for adjustment in self.adjustments:
            gainloss = adjustment.gainloss
            if gainloss != 0.0:
                account = adjustment.account
                name = 'UGL: %s' % self.close_date
                ref = 'AC: %s-%s' % (account.code, account.name)
                with get_creator(Move) as creator:
                    creator.update(
                        name=name,
                        ref=ref,
                        journal_id=self.journal_id.id,
                        period_id=Period.find(dt=self.close_date).id,
                        date=self.close_date,
                    )
                    if gainloss > 0:
                        creator.create(
                            'line_id',
                            name=name,
                            account_id=self.gain_account_id.id,
                            credit=gainloss
                        )
                        creator.create(
                            'line_id',
                            name=name,
                            account_id=account.id,
                            debit=gainloss,
                            amount_currency=0,
                            currency_id=account.currency_id.id
                        )
                    else:
                        creator.create(
                            'line_id',
                            name=name,
                            account_id=self.loss_account_id.id,
                            debit=-gainloss
                        )
                        creator.create(
                            'line_id',
                            name=name,
                            account_id=account.id,
                            credit=-gainloss,
                            amount_currency=0,
                            currency_id=account.currency_id.id
                        )


class Adjustment(models.TransientModel):
    _name = 'xopgi.unrealized_gl_adjustment'

    wizard = fields.Many2one('xopgi.unrealized_gl_wizard')
    account = fields.Many2one('account.account')

    account_name = fields.Char(related="account.name")
    account_code = fields.Char(related="account.code")
    account_currency = fields.Many2one(related="account.currency_id")

    foreign_balance = fields.Float(compute='_compute_all')
    balance = fields.Float(compute='_compute_all')
    adjusted_balance = fields.Float(compute='_compute_all')
    gainloss = fields.Float(compute='_compute_all')

    @api.depends('account', 'wizard')
    def _compute_all(self):
        precision = DecimalPrecision.precision_get('Account')
        company_currency = self.env.user.company_id.currency_id
        for record in self:
            account = record.account
            close_date = record.wizard.close_date
            data = account._account_account__compute(
                field_names=('balance', 'foreign_balance'),
                query="l.date <= '" + close_date + "'"
            )
            get = lambda v: data[account.id][v]
            record.balance = get('balance')
            record.foreign_balance = get('foreign_balance')
            record.adjusted_balance = account.currency_id.with_context(date=close_date).compute(
                record.foreign_balance,
                company_currency,
                round=False,
            )
            record.gainloss = round(
                record.adjusted_balance - record.balance,
                precision
            )
