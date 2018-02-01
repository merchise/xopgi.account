#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

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
        "wizard/view/unrealized_gl_wizard.xml",
    ],
    installable=10 <= MAJOR_ODOO_VERSION < 11,   # noqa
)
