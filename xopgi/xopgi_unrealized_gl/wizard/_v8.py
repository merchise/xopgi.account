#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# _v8
# ---------------------------------------------------------------------
# Copyright (c) 2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2017-08-22

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoeuf import api
from xoeuf.models.proxy import DecimalPrecision


@api.depends('account', 'wizard')
def _compute_all(self):
    precision = DecimalPrecision.precision_get('Account')
    company_currency = self.env.user.company_id.currency_id
    for record in self:
        account = record.account
        close_date = record.wizard.close_date
        # The 'l' alias in the SQL query refers to the move line.
        data = account.with_context(state='posted')._account_account__compute(
            field_names=('balance', 'foreign_balance'),
            # Why do I need to filter line's date instead of the move's.
            # Is this consistent with the Chart of Account report, and
            # other reports?
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
