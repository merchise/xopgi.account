#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# pre-001-cleanup-db
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-06-08

'''Drop the line_currency_amount column so that previous data is invalidated.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


def migrate(cr, version):
    cr.execute('''
       ALTER TABLE account_move_line
         DROP COLUMN IF EXISTS line_currency_amount;
    ''')
