#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from __future__ import division, print_function, absolute_import

from odoo import _
from xoeuf import api, models
from xoeuf.osv.orm import CREATE_RELATED

from .config import get_account_config


class AccountAdvanceInvoice(models.Model):
    _inherit = 'account.invoice'

    @property
    def _matching_advancement_account_type(self):
        '''The account type for advancements of the invoice's type.'''
        config = get_account_config(self)
        if self.type == 'out_invoice':
            type = config.advanced_receivable_type_id
        elif self.type == 'in_invoice':
            type = config.advanced_payable_type_id
        else:
            type = None
        return type

    @api.requires_singleton
    def match_advance_account(self, pre_account_id, amount):
        '''Match a given amount for the `pre_account_id`.

        It can be a pre-payment or a pre-collection.  This depends solely on
        the type of the invoice.

        '''
        AccountMove = self.env['account.move']
        Account = self.env['account.account']
        pre_account = Account.browse(pre_account_id)
        if self.type == 'out_invoice':
            return AccountMove._match_precollection(
                self.move_id,
                pre_account,
                amount,
                currency=self.currency_id
            )
        elif self.type == 'in_invoice':
            return AccountMove._match_prepayment(
                self.move_id,
                pre_account,
                amount,
                currency=self.currency_id
            )
        else:
            return False

    @api.requires_singleton
    def _get_advancement_accounts(self):
        type = self._matching_advancement_account_type
        if type:
            Account = self.env['account.account']
            if self.currency_id:
                return Account.search([
                    ('user_type_id', '=', type.id),
                    '|',
                    ('currency_id', '=', False),
                    ('currency_id', '=', self.currency_id.id),
                ])
            else:
                return Account.search([
                    ('user_type_id', '=', type.id),
                    ('currency_id', '=', False),
                ])
        else:
            return Account.browse()

    @api.model
    def get_advancement_accounts_by_type_id(self, account_type_id):
        """Return pre-payments|pre-collection accounts that are registered
        in account.account model"""
        return self.env['account.account'].search([
            ('user_type_id', '=', account_type_id)
        ])

    @api.model
    def _get_normal_balance(self, pre_account, account_type):
        return account_type.get_balance(
            pre_account,
            currency=self.currency_id,
            conditions=dict(
                partner_id=self.partner_id.id,
            )
        )

    @property
    def _advancements(self):
        '''The possible advancement to match.'''
        from .normal_balance import get_account_normal_type
        if self.state != 'open':
            return []
        advancements = []
        accounts = self._get_advancement_accounts()
        for pre_account in accounts:
            amount = self._get_normal_balance(
                pre_account,
                get_account_normal_type(pre_account),
            )
            if amount:
                advancements.append({
                    'id': pre_account.id,
                    'journal_name': pre_account.name,
                    'amount': amount,
                    'max_reduction': min(self.residual, amount),
                    'currency_symbol': self.currency_id.symbol,
                    'position': self.currency_id.position,
                    # TODO: What does 69 mean?
                    'digits': [69, self.currency_id.decimal_places],
                })
        return advancements


def _is_payable(account):
    return account.user_type_id.type == 'payable'


def _is_payable_line(line):
    return _is_payable(line.account_id)


def _is_receivable(account):
    return account.user_type_id.type == 'receivable'


def _is_receivable_line(line):
    return _is_receivable(line.account_id)


class AdvancedAccountMove(models.Model):
    _inherit = 'account.move'

    @api.requires_singleton
    def _match_prepayment(self, invoice_move, pre_account, amount,
                          currency=False):
        '''Create a matching entry for a prepayment and reconciles it.

        `amount` is the amount to match expressed in `currency`.  If
        `currency` is False, it defaults to the invoice's company currency.

        '''
        if currency and currency == invoice_move.company_id.currency_id:
            # We must not set the currency if it's the same as the company's
            currency_id = False
        else:
            currency_id = currency.id
        payable_line = invoice_move.line_ids.filtered(_is_payable_line)
        assert len(payable_line) == 1
        config = get_account_config(self)
        journal = config.prepayment_journal_type_id
        date = invoice_move.date
        res = self.create(dict(
            date=date,
            line_ids=[
                CREATE_RELATED(
                    name=_('Prepayment: {0}').format(invoice_move.name),
                    currency_debit=amount,
                    currency_credit=0,
                    currency_id=currency_id,
                    partner_id=invoice_move.partner_id.id,
                    account_id=payable_line.account_id.id,
                    date=date,
                ),
                CREATE_RELATED(
                    name=_('Prepayment: {0}').format(invoice_move.name),
                    currency_credit=amount,
                    currency_debit=0,
                    currency_id=currency_id,
                    partner_id=invoice_move.partner_id.id,
                    account_id=pre_account.id,
                    date=date,
                ),
            ],
            narratation=_("From prepayment {move}").format(
                move=invoice_move.name or invoice_move.ref
            ),
            journal_id=journal.id,
        ))
        res.post()
        matching_line = res.line_ids.filtered(
            lambda l: l.account_id == payable_line.account_id
        )
        lines = payable_line + matching_line
        lines.reconcile()

    def _match_precollection(self, invoice_move, pre_account, amount,
                             currency=False):
        '''Create a matching entry for a precollection.

        The meaning of the parameters is the same that in
        `_match_prepayment`:meth:

        '''
        config = get_account_config(self)
        journal = config.precollection_journal_type_id
        if currency and currency == invoice_move.company_id.currency_id:
            # We must not set the currency if it's the same as the company's
            currency_id = False
        else:
            currency_id = currency.id
        receivable_line = invoice_move.line_ids.filtered(_is_receivable_line)
        assert len(receivable_line) == 1
        date = invoice_move.date
        res = self.create(dict(
            date=date,
            line_ids=[
                CREATE_RELATED(
                    name=_('Precollection: {0}').format(invoice_move.name),
                    currency_credit=amount,
                    currency_debit=0,
                    currency_id=currency_id,
                    partner_id=invoice_move.partner_id.id,
                    account_id=receivable_line.account_id.id,
                    date=date,
                ),
                CREATE_RELATED(
                    name=_('Precollection: {0}').format(invoice_move.name),
                    currency_debit=amount,
                    currency_credit=0,
                    currency_id=currency_id,
                    partner_id=invoice_move.partner_id.id,
                    account_id=pre_account.id,
                    date=date,
                ),
            ],
            narratation=_("From pre-collection {move}").format(
                move=invoice_move.name or invoice_move.reference
            ),
            journal_id=journal.id
        ))
        res.post()
        matching_line = res.line_ids.filtered(
            lambda l: l.account_id == receivable_line.account_id
        )
        lines = receivable_line + matching_line
        lines.reconcile()
