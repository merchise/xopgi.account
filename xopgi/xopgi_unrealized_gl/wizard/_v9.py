#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# _v9
# ---------------------------------------------------------------------
# Copyright (c) 2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2017-08-23

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoeuf import api
from xoeuf.models.proxy import DecimalPrecision, AccountMoveLine


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
