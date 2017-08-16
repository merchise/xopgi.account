# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi.addons.account
# ---------------------------------------------------------------------
# Copyright (c) 2013-2017 Merchise Autrement [~º/~]
# All rights reserved.
#
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# @created: 2013-11-11
# flake8:  noqa

from xoeuf import MAJOR_ODOO_VERSION


if MAJOR_ODOO_VERSION < 10:
    # Not tested in Odoo 10
    from . import config


if MAJOR_ODOO_VERSION < 9:
    # The Chart of Accounts wizard no longer exists in Odoo 9.
    from . import chart

    # The following contain only UI-level modifications that are no longer
    # compatible with Odoo 9.
    from . import move
    from . import voucher
    from . import misc

    # Odoo 9 has its own 'Post Journal Entries' to post multiple entries at
    # once.
    from . import post

if MAJOR_ODOO_VERSION < 10:
    # Not tested in Odoo 10
    from . import invoice
    from . import reconcile

if MAJOR_ODOO_VERSION < 11:
    from . import track
