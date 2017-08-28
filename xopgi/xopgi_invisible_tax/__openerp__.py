#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# __openerp__
# ---------------------------------------------------------------------
# Copyright (c) 2014-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2014-12-18

{
    "name": "xopgi_invisible_tax",
    "version": "2.0",
    "author": "Merchise Autrement",
    "website": "http://xopgi.merchise.org/addons/xopgi_account",
    "category": "Hidden",
    "description": "Hides tax column when editing journal items.",
    "depends": [
        'xopgi_account',
    ],
    "data": [
        'views/%d/tax.xml' % MAJOR_ODOO_VERSION,  # noqa
    ],
    "application": False,
    'installable': 8 <= MAJOR_ODOO_VERSION < 11,   # noqa
}
