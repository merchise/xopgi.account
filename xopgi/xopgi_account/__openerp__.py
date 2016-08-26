# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi.xopgi_account.__openerp__
# ---------------------------------------------------------------------
# Copyright (c) 2013-2016 Merchise Autrement [~º/~]
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# @created: 2013-11-11


{
    "name": "Accounting (extended - xopgi)",
    "version": "1.15",
    "author": "Merchise Autrement",
    "website": "http://xopgi.merchise.org/addons/xopgi_account",
    "category": "Accounting",
    "description": "Accounting",
    "depends": ['account_accountant', 'analytic', 'account', ],
    "data": [
        'view/config.xml',
        'view/company.xml',
        'view/account.xml',
        'view/filters.xml',
        'view/posting.xml',
        'view/reconcile.xml',
        'static/assets.xml',
    ],
    "application": False,
    "installable": True,
}
