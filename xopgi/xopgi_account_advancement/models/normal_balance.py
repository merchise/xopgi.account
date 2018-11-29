#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from __future__ import division, print_function, absolute_import

from xoeuf.odoo.tools import float_precision


# TODO: Create the normal balance classification of accounts.
class ACCOUNT:
    @classmethod
    def select_type(cls, account):
        '''Get the real type of the account.'''
        from .config import get_account_config
        config = get_account_config(account)
        if account.user_type_id == config.advanced_receivable_type_id:
            return CREDIT_ACCOUNT
        elif account.user_type_id == config.advanced_payable_type_id:
            return DEBIT_ACCOUNT
        else:
            assert False

    @classmethod
    def credit(cls, account, counter_part, amount, currency):
        pass

    @classmethod
    def debit(cls, account, counter_part, amount, currency):
        pass


get_account_normal_type = ACCOUNT.select_type


class CREDIT_ACCOUNT(ACCOUNT):
    @classmethod
    def get_balance(cls, account, disallow_negative=True,
                    currency=None, conditions=None):
        # CREDIT is just DEBIT negated; but we need to *allow* negative
        # results so that we get the balance and deal with disallow_negative
        # ourselves.  Summary: don't change disallow_negative=False below!
        amount = -DEBIT_ACCOUNT.get_balance(
            account,
            disallow_negative=False,
            currency=currency,
            conditions=conditions
        )
        if not disallow_negative or amount >= 0:
            return amount
        else:
            return 0

    @classmethod
    def increase(cls, account, counterpart, amount, currency):
        return cls.credit(account, counterpart, amount, currency)

    @classmethod
    def decrease(cls, account, counterpart, amount, currency):
        return cls.debit(account, counterpart, amount, currency)


class DEBIT_ACCOUNT(ACCOUNT):
    @classmethod
    def get_balance(cls, account, disallow_negative=True,
                    currency=None, conditions=None):
        cr = account.env.cr
        if not conditions:
            conditions = {
                'account_id': account.id
            }
        else:
            conditions['account_id'] = account.id
        where = ' AND '.join(
            '{key}=%({key})s'.format(key=key)
            for key in conditions
        )
        cr.execute('''
            SELECT COALESCE(SUM(debit) - SUM(credit), 0) AS amount
            FROM account_move_line
            WHERE {}'''.format(where), conditions)
        result = cr.fetchall()
        amount = result[0][0]
        if currency and account.company_id.currency_id != currency:
            amount = account.company_id.currency_id.compute(
                amount,
                currency,
            )
        elif currency:
            amount = float_precision(
                currency.round(amount),
                currency.decimal_places
            )
        if not disallow_negative or amount >= 0:
            return amount
        else:
            return 0

    @classmethod
    def increase(cls, account, counterpart, amount, currency):
        return cls.debit(account, counterpart, amount, currency)

    @classmethod
    def decrease(cls, account, counterpart, amount, currency):
        return cls.credit(account, counterpart, amount, currency)
