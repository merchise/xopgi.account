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
    "name": "xopgi_invisible_tax",
    "version": "1.15",
    "author": "Merchise Autrement",
    "website": "http://xopgi.merchise.org/addons/xopgi_account",
    "category": "Hidden",
    "description": "Hides tax column when editing journal items.",
    "depends": [
        'xopgi_account',
    ],
    "data": [
        'tax.xml',
    ],
    "demo_xml": [],
    "application": False,
    "installable": True,
}
