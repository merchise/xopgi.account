#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# __openerp__
# ---------------------------------------------------------------------
# Copyright (c) 2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#

dict(
    name="Generate payment (voucher) from invoices",
    author="Merchise Autrement",
    category='Accounting & Finance',
    version='1.0',
    depends=[
        'base',
        'account'
    ] + (['account_voucher'] if MAJOR_ODOO_VERSION < 9 else []),  # noqa
    data=[
        "views/%d/account_voucher_views.xml" % MAJOR_ODOO_VERSION,  # noqa
        "wizard/%d/voucher_wizard.xml" % MAJOR_ODOO_VERSION,  # noqa
    ],

    # Since Odoo 9, it quite unused.  Odoo 9 and 10 have the option to create
    # a payment from invoices directly.  We mark it ready to ease the
    # migration.
    installable=8 <= MAJOR_ODOO_VERSION < 11,   # noqa
)
