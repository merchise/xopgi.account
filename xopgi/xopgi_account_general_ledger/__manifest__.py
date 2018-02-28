#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

dict(
    name="Filter General Ledger (extended - xopgi)",
    author="Merchise Autrement",
    category="Accounting",
    description="Allow filter by accounts in general ledger report.",
    depends=[
        'account'
    ],
    data=[
        'wizard/account_report_general_ledger_view.xml',
    ],
    application=False,
    installable=10 <= MAJOR_ODOO_VERSION < 11,   # noqa
)
