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

try:
    from openerp.release import version_info as ODOO_VERSION_INFO
except ImportError:
    # This is Odoo 10+, but let's be able to get the ODOO_VERSION_INFO
    from odoo.release import version_info as ODOO_VERSION_INFO


if ODOO_VERSION_INFO < (10, 0):
    # Not tested in Odoo 10
    from . import config


if ODOO_VERSION_INFO < (9, 0):
    # The Chart of Accounts wizard no longer exists in Odoo 9.
    from . import chart

    # The following contain only UI-level modifications that are no longer
    # compatible with Odoo 9.
    from . import move
    from . import voucher
    from . import misc

if ODOO_VERSION_INFO < (10, 0):
    # Not tested in Odoo 10
    from . import invoice
    from . import multicompanyitem
    from . import currency
    from . import post
    from . import reconcile
    from . import analytic
    from . import track
