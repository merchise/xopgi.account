#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

dict(
    name="Summarize Account Partner Balance (extended - xopgi)",
    version="1.16",
    author="Merchise Autrement",
    category="Accounting",
    description="Adds graphs for receivables and payables with currency.",
    depends=[
        'account',
        'xopgi_proper_currency'
    ],
    data=[
        'view/partners.xml',
    ],
    application=False,
    installable=10 <= MAJOR_ODOO_VERSION < 11,   # noqa
)
