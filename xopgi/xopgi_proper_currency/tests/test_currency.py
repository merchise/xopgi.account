#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

import datetime
from xoeuf.odoo.addons.account.tests.account_test_classes import AccountingTestCase


class TestCurrency(AccountingTestCase):
    def setUp(self):
        super(TestCurrency, self).setUp()
        Account = self.env['account.account']
        Journal = self.env['account.journal']
        self.Move = self.env['account.move']
        self.company = self.env.ref('base.main_company')
        self.other_currency = self.env['res.currency'].search(
            [('id', '!=', self.company.currency_id.id)],
            limit=1
        )
        self.partner = self.env.ref('base.res_partner_2')
        self.bank_account = Account.search(
            [('user_type_id', '=', self.env.ref('account.data_account_type_liquidity').id)],
            limit=1
        )
        self.receivable_account = Account.search(
            [('user_type_id', '=', self.env.ref('account.data_account_type_receivable').id)],
            limit=1
        )
        self.journal = Journal.create({
            'name': 'Bank',
            'type': 'bank',
            'code': 'BNK67'
        })
        self.date = datetime.datetime.now()

    def test_company_currency_is_never_saved(self):
        from xoeuf.osv.orm import CREATE_RELATED
        assert self.journal
        res = self.Move.create(dict(
            date=self.date,
            line_ids=[
                CREATE_RELATED(
                    name='Testing/Bank/001',
                    currency_debit=1000,
                    currency_credit=0,
                    currency_id=self.company.currency_id.id,
                    partner_id=self.partner.id,
                    account_id=self.bank_account.id,
                    date=self.date
                ),
                CREATE_RELATED(
                    name='Testing/Bank/001',
                    currency_debit=0,
                    currency_credit=1000,
                    currency_id=self.company.currency_id.id,
                    partner_id=self.partner.id,
                    account_id=self.receivable_account.id,
                    date=self.date
                )
            ],
            journal_id=self.journal.id
        ))
        for line in res.line_ids:
            self.assertFalse(line.currency_id)

    def test_other_currency_is_saved(self):
        from xoeuf.osv.orm import CREATE_RELATED
        assert self.journal
        res = self.Move.create(dict(
            date=self.date,
            line_ids=[
                CREATE_RELATED(
                    name='Testing/Bank/001',
                    currency_debit=1000,
                    currency_credit=0,
                    currency_id=self.other_currency.id,
                    partner_id=self.partner.id,
                    account_id=self.bank_account.id,
                    date=self.date
                ),
                CREATE_RELATED(
                    name='Testing/Bank/001',
                    currency_debit=0,
                    currency_credit=1000,
                    currency_id=self.other_currency.id,
                    partner_id=self.partner.id,
                    account_id=self.receivable_account.id,
                    date=self.date
                )
            ],
            journal_id=self.journal.id
        ))
        for line in res.line_ids:
            self.assertEqual(line.currency_id, self.other_currency)
