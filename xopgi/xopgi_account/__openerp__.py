# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi.xopgi_account.__openerp__
# ---------------------------------------------------------------------
# Copyright (c) 2013-2015 Merchise Autrement
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# @created: 2013-11-11


{
    "name": "Accounting (extended - xopgi)",
    "version": "1.13",
    "author": "Merchise Autrement",
    "website": "http://xopgi.merchise.org/addons/xopgi_account",
    "category": "Accounting",
    "description": "Accounting",
    "depends": ['account_accountant'],
    "data": [
        'view/config.xml',
        'view/company.xml',
        'view/account.xml',
        'view/filters.xml',
        'view/posting.xml',
        'view/reconcile.xml',
        (
            'view/7/account.xml'
            if ODOO_VERSION_INFO < (8, 0)  # noqa
            else 'dummy.xml'
        ),
        (
            'static/assets.xml'
            if ODOO_VERSION_INFO >= (8, 0)  # noqa
            else 'dummy.xml'
        ),
    ],
    # TODO: [review ~med] Where to place UI enhancements.  Proposal xopgi_ui.
    "css": ["static/src/css/xopgi_account.css", ],
    "js": ["static/src/js/reconciliation.js"],
    "application": False,
    "installable": True,
}
