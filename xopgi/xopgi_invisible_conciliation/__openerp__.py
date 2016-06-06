#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# __openerp__
# ---------------------------------------------------------------------
# Copyright (c) 2014-2016 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2014-12-18

{
    "name": "xopgi_invisible_tax",
    "version": "1.15",
    "author": "Merchise Autrement",
    "website": "http://xopgi.merchise.org/addons/xopgi_account",
    "category": "Hidden",
    "description": "Hides conciliation columns when editing journal items.",
    "depends": ['account_accountant'],
    "data": [
        'conciliate.xml',
    ],
    "demo_xml": [],
    "application": False,
    'installable': (8, 0) <= ODOO_VERSION_INFO < (9, 0),   # noqa
}
