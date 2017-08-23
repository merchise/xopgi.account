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
# Created on 2017-08-18

dict(
    name="Unrealized Gain & Loss",
    author="Merchise Autrement",
    category="Accounting",
    version="1.0",
    depends=[
        "base",
        "account"
    ],
    data=[
        "settings/view.xml",
        "wizard/view/%d/unrealized_gl_wizard.xml" % MAJOR_ODOO_VERSION,  # noqa
    ],
    installable=8 <= MAJOR_ODOO_VERSION < 11,   # noqa
)
