#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

from xoeuf import MAJOR_ODOO_VERSION


if MAJOR_ODOO_VERSION < 11:
    # Not tested in Odoo 10
    from . import config  # noqa


if MAJOR_ODOO_VERSION < 9:
    # The Chart of Accounts wizard no longer exists in Odoo 9.
    from . import chart  # noqa

    # The following contain only UI-level modifications that are no longer
    # compatible with Odoo 9.
    from . import move  # noqa
    from . import voucher  # noqa
    from . import misc  # noqa

    # Odoo 9 has its own 'Post Journal Entries' to post multiple entries at
    # once.
    from . import post  # noqa

if MAJOR_ODOO_VERSION < 11:
    from . import invoice  # noqa
    from . import reconcile  # noqa
    from . import track  # noqa
