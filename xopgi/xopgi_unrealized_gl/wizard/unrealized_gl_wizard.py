#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Perform the Unrealized Gain/Loss adjustment.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoeuf import api, fields, models
from xoeuf.models.extensions import get_creator
from xoeuf.models.proxy import (
    DecimalPrecision,
    AccountMoveLine,
    AccountMove as Move,
    AccountAccount as Account,
    ResCurrency as Currency,
)

from xoeuf.osv.orm import CREATE_RELATED

from ..settings import REGULAR_ACCOUNT_DOMAIN, GENERAL_JOURNAL_DOMAIN


LINES_FIELD_NAME = 'line_ids'


def _get_valid_accounts(currency=None):
    if currency is None:
        query = [("currency_id", "!=", False)]
    else:
        query = [("currency_id", "=", currency.id)]
    return Account.search(query)


def next_seq(s):
    return s.next_by_id()


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
        domain=GENERAL_JOURNAL_DOMAIN,
        default=_get_journal,
        readonly=True
    )

    gain_account_id = fields.Many2one(
        "account.account",
        string="Gain Account",
        required=True,
        domain=REGULAR_ACCOUNT_DOMAIN,
        default=_get_gain_account,
        readonly=True
    )

    loss_account_id = fields.Many2one(
        "account.account",
        string="Loss Account",
        required=True,
        domain=REGULAR_ACCOUNT_DOMAIN,
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
                currency = record.currency_id.with_context(date=self.close_date)
                record.currency_rate = currency.compute(
                    1,
                    company_currency,
                    round=False,
                )
                accounts = _get_valid_accounts(record.currency_id)
                adjustments = [
                    CREATE_RELATED(account=account, wizard=record)
                    for account in accounts
                ]
                record.adjustments = adjustments

    @api.multi
    def generate(self):
        from xoeuf.models.extensions import get_treeview_action
        moves = self._do_generate()
        return get_treeview_action(moves)

    @api.multi
    def _do_generate(self):
        moves = Move.browse()
        for adjustment in self.adjustments:
            gainloss = adjustment.gainloss
            if gainloss:
                sequence = self.journal_id.sequence_id
                account = adjustment.account
                name = 'UGL: %s' % self.close_date
                ref = 'UGL for AC: %s-%s at %s' % (account.code, account.name,
                                                   self.close_date)
                with get_creator(Move) as creator:
                    creator.update(
                        name=next_seq(sequence),
                        ref=ref,
                        journal_id=self.journal_id.id,
                        date=self.close_date,
                    )
                    if gainloss > 0:
                        creator.create(
                            LINES_FIELD_NAME,
                            name=name,
                            account_id=self.gain_account_id.id,
                            credit=gainloss
                        )
                        creator.create(
                            LINES_FIELD_NAME,
                            name=name,
                            account_id=account.id,
                            debit=gainloss,
                            amount_currency=0,
                            currency_id=account.currency_id.id
                        )
                    else:
                        creator.create(
                            LINES_FIELD_NAME,
                            name=name,
                            account_id=self.loss_account_id.id,
                            debit=-gainloss
                        )
                        creator.create(
                            LINES_FIELD_NAME,
                            name=name,
                            account_id=account.id,
                            credit=-gainloss,
                            amount_currency=0,
                            currency_id=account.currency_id.id
                        )

                # outside the with we get the result
                moves |= creator.result
        return moves


class Adjustment(models.TransientModel):
    _name = 'xopgi.unrealized_gl_adjustment'

    wizard = fields.Many2one('xopgi.unrealized_gl_wizard')
    account = fields.Many2one('account.account')

    account_name = fields.Char(related="account.name")
    account_code = fields.Char(related="account.code")
    account_currency = fields.Many2one(related="account.currency_id")

    foreign_balance = fields.Float(compute='_compute_all', default=0)
    balance = fields.Float(compute='_compute_all', default=0)
    adjusted_balance = fields.Float(compute='_compute_all', default=0)
    gainloss = fields.Float(compute='_compute_all', default=0)

    @api.depends('account', 'wizard')
    def _compute_all(self):
        precision = DecimalPrecision.precision_get('Account')
        company_currency = self.env.user.company_id.currency_id
        # Map records to accounts so that we can compute the balances in a single
        # DB query
        account_map = dict(zip(self.mapped('account.id'), self))
        assert len(account_map) == len(self)
        close_date = self[0].wizard.close_date
        tables, where_clause, where_params = AccountMoveLine.with_context(
            state='posted', date_to=close_date
        )._query_get()
        if not tables:
            tables = '"account_move_line"'
        if where_clause.strip():
            filters = [where_clause]
        else:
            filters = []
        filters.append('"account_move_line"."account_id" IN %s')
        where_params.append(tuple(account_map.keys()))
        query = ('''
            SELECT account_id AS id,
                   COALESCE(SUM(debit), 0) - COALESCE(SUM(credit), 0) AS balance,
                   COALESCE(SUM(amount_currency), 0) as foreign_balance
               FROM {tables}
               WHERE {filters}
               GROUP BY account_id
        ''').format(tables=tables, filters=' AND '.join(filters))
        self.env.cr.execute(query, where_params)
        for row in self.env.cr.dictfetchall():
            record = account_map.pop(int(row['id']))  # cast to int, otherwise KeyError
            account = record.account
            record.balance = balance = row['balance']
            record.foreign_balance = row['foreign_balance']
            record.adjusted_balance = adjusted = account.currency_id.with_context(date=close_date).compute(
                record.foreign_balance,
                company_currency,
                round=False,
            )
            record.gainloss = round(adjusted - balance, precision)
        for record in account_map.values():
            record.balance = record.foreign_balance = 0
            record.adjusted_balance = record.gainloss = 0
