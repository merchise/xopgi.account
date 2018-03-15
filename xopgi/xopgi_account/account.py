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

from xoeuf import fields, models
from xoeuf.odoo.tools import float_precision


class Account(models.Model):
    _inherit = 'account.account'

    @fields.Property
    def balance(self):
        cr = self.env.cr
        # Faster with SQL
        cr.execute('''
           SELECT COALESCE(SUM(debit) - SUM(credit), 0) AS balance
           FROM account_move_line WHERE account_id=%s
        ''', (self.id, ))
        rows = cr.fetchall()
        if not rows:
            return 0
        result = rows[0][0]
        currency = self.company_id.currency_id
        if currency:
            return float_precision(currency.round(result), currency.decimal_places)
        else:
            return result
