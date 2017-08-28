#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# unrealized_gl_wizard
# ---------------------------------------------------------------------
# Copyright (c) 2015-2017 Merchise Autrement [~º/~] and Contributors
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

from xoeuf import api, fields, models, MAJOR_ODOO_VERSION
from xoeuf.models.extensions import get_creator
from xoeuf.models.proxy import (
    AccountPeriod as Period,
    AccountMove as Move,
    AccountAccount as Account,
    ResCurrency as Currency,
)

from xoeuf.osv.orm import CREATE_RELATED

from ..settings import REGULAR_ACCOUNT_DOMAIN, GENERAL_JOURNAL_DOMAIN


if MAJOR_ODOO_VERSION < 9:
    LINES_FIELD_NAME = 'line_id'

    def _get_valid_accounts(currency=None):
        query = [("type", "!=", "view")]
        if currency is None:
            query += [("currency_id", "!=", False)]
        else:
            query += [("currency_id", "=", currency.id)]
        return Account.search(query)

    def next_seq(s):
        # It seems that Odoo 8, regards `next_by_id` as an api.model instead
        # of api.multi
        return s.next_by_id(s.id)

else:
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
                    if MAJOR_ODOO_VERSION < 9:
                        creator.update(
                            period_id=Period.find(dt=self.close_date).id,
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

    if MAJOR_ODOO_VERSION < 9:
        from ._v8 import _compute_all
    elif 9 <= MAJOR_ODOO_VERSION < 11:
        from ._v9 import _compute_all
