#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

from xoeuf import MAJOR_ODOO_VERSION


if 10 <= MAJOR_ODOO_VERSION < 11:
    from . import models  # noqa
    from .models.config import DEFAULT_ACCOUNT_TYPES  # noqa
    from . import _ui  # noqa
