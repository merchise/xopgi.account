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
# Created on 2017-08-16


dict(
    name='xopgi_show_journal_items',
    version='1.0',
    author="Merchise Autrement",
    website="http://merchise-autrement.gitlab.io/xopgi/",
    category="Hidden",
    depends=['xopgi_account', 'account', ],
    data=[
        'view/%d/menu.xml' % MAJOR_ODOO_VERSION,  # noqa
    ],
    application=False,

    # This is because we like to see journal items but Odoo 9 and 10, keep
    # them invisible unless 'debug=1'.
    installable=9 <= MAJOR_ODOO_VERSION < 11,   # noqa

    auto_install=False,

)
