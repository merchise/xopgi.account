#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

dict(
    name='xopgi_account_celery',
    version="2.0",
    author="Merchise Autrement",
    website="http://merchise-autrement.gitlab.io/xopgi/",
    category="Hidden",
    depends=[
        'account',
        'web_celery'
    ],
    data=[
        'views/invoice.xml',
        'views/move.xml',
    ],
    application=False,
    installable=10 <= MAJOR_ODOO_VERSION < 11,   # noqa
    auto_install=True,
)
