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
# Created on 2017-02-09

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
        'views/%d/validate.xml' % MAJOR_ODOO_VERSION,  # noqa
    ],
    application=False,
    installable=8 <= MAJOR_ODOO_VERSION < 11,   # noqa
    auto_install=True,
)
