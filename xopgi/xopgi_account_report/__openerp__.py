# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi.xopgi_account_report
# ---------------------------------------------------------------------
# Copyright (c) 2013-2015 Merchise Autrement
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# @created: 2015-03-26


{
    "name": "Summarize Account Partner Balance (extended - xopgi)",
    "version": "1.9",
    "author": "Merchise Autrement",
    "website": "http://xopgi.merchise.org/addons/xopgi_account",
    "category": "Accounting",
    "description": "Accounting",
    "depends": ['account', 'report_webkit'],
    "data": [
        'data/financial_webkit_header.xml',
        'report/report.xml',
        'view/summarize_partner_balance_wizard_view.xml'
    ],
    "application": False,
    "installable": True,
}
