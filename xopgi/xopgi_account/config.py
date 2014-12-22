#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_account.config
# ---------------------------------------------------------------------
# Copyright (c) 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2014-12-18

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from openerp.osv import fields
from openerp.osv.orm import TransientModel


class AccountConfigSettings(TransientModel):
    _name = str('account.config.settings')
    _inherit = _name

    _columns = {
        'module_xopgi_invisible_tax':
            fields.boolean('Hide account tax column when editing journal '
                           'items.'),

        'module_xopgi_invisible_conciliation':
            fields.boolean('Hides conciliation columns when editing journal '
                           'items.'),
    }
