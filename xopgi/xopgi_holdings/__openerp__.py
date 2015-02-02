#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# __openerp__
# ---------------------------------------------------------------------
# Copyright (c) 2014, 2015 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2014-12-18

{
    "name": "Accounting for holdings (xopgi)",
    "version": "1.7",
    "author": "Merchise Autrement",
    "website": "http://xopgi.merchise.org/addons/xopgi_account",
    "category": "Accounting",
    "description": """
Accounting for Holdings
=======================

Allows to do accounting for each company controlled by a single holding.  Each
company does its accounting in its own currency, while the holding
consolidates the reports.

""",
    "depends": ['xopgi_account'],
    "data": [
        'view/chart.xml',
    ],
    "demo_xml": [],
    # TODO: [review ~med] Where to place UI enhancements.  Proposal xopgi_ui.
    "application": False,
    "installable": True,
}
