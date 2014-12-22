# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# xopgi.xopgi_account.__openerp__
#----------------------------------------------------------------------
# Copyright (c) 2013, 2014 Merchise Autrement
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# @created: 2013-11-11


{
    "name": "Accounting (extended - xopgi)",
    "version": "1.8",
    "author": "Merchise Autrement",
    "website": "http://xopgi.merchise.org/addons/xopgi_account",
    "category": "Accounting",
    "description": "Accounting",
    "depends": ['account_accountant'],
    "init_xml": [],
    "update_xml": [
        'view/config.xml',
        'view/company.xml',
        'view/account.xml',
        'view/filters.xml',
    ],
    "demo_xml": [],
    # TODO: [review ~med] Where to place UI enhancements.  Proposal xopgi_ui.
    "css": ["static/css/xopgi_account.css", ],
    "application": False,
    "installable": True,
}
