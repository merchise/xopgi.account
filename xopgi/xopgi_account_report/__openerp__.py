# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi.xopgi_account_report
# ---------------------------------------------------------------------
# Copyright (c) 2013-2016 Merchise Autrement
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# @created: 2015-03-26


dict(
    name="Summarize Account Partner Balance (extended - xopgi)",
    version="1.16",
    author="Merchise Autrement",
    category="Accounting",
    description="Adds graphs for receivables and payables with currency.",
    depends=['account', 'xopgi_proper_currency'],
    data=[
        'view/partners.xml'
    ],
    application=False,
    installable=True,
)
