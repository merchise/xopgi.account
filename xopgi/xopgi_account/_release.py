#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi.addons.account._release
# ---------------------------------------------------------------------
# Copyright (c) 2013-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2014-04-24


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_imports)


def read_terpfile():
    import os
    with open(os.path.join(os.path.dirname(__file__), '__openerp__.py'), 'rU') as fh:
        content = fh.read()
        return eval(content, {'MAJOR_ODOO_VERSION': 8}, {})

_TERP = read_terpfile()
VERSION = _TERP['version']
