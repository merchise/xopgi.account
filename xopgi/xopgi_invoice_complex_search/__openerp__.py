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
# Created on 2017-08-24

dict(
    name="Invoice Complex Search",
    version='1.0',
    depends=['account'],
    author="Merchise Autrement",
    category='Accounting & Finance',
    data=['views/invoice.xml'],
    installable=8 <= MAJOR_ODOO_VERSION < 11,   # noqa
)
