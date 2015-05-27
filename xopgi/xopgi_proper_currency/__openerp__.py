#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# __openerp__
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-01-08

dict(
    name='xopgi_proper_currency',
    version="1.10",
    author="Merchise Autrement",
    website="http://merchise-autrement.gitlab.io/xopgi/",
    category="Hidden",
    description=("Usability improvements for accounting with foreign "
                 "currencies."),
    depends=['xopgi_account'],
    data=[
        'view/moves.xml',
        'view/invoices.xml',
    ],
    application=False,
    installable=True,
    auto_install=True,
)
