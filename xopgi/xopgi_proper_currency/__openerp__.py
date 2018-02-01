#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

dict(
    name='xopgi_proper_currency',
    version="1.16",
    author="Merchise Autrement",
    website="http://merchise-autrement.gitlab.io/xopgi/",
    category="Hidden",
    description=("Usability improvements for accounting with foreign "
                 "currencies."),
    depends=['account', 'account_accountant'],
    data=[
        'view/moves.xml',
        'view/invoices.xml',
    ],
    application=False,
    installable=10 <= MAJOR_ODOO_VERSION < 11,   # noqa
    auto_install=False,
)
