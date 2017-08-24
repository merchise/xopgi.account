#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# __openerp__
# ---------------------------------------------------------------------
# Copyright (c) 2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#

dict(
    name="Generate payment (voucher) from invoices",
    author="Merchise Autrement",
    category='Accounting & Finance',
    version='1.0',
    depends=['base', "account_voucher"],
    data=[
        "views/account_voucher_views.xml",
        "wizard/voucher_wizard.xml"
    ],
    installable=8 <= MAJOR_ODOO_VERSION < 9,   # noqa
)
