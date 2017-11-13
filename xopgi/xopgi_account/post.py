#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Allows to post several moves in a single click.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoeuf import api, models


class PostMoveConfirmation(models.TransientModel):
    _name = 'xopgi.account.move.confirm'

    @api.multi
    def post(self):
        Move = self.env['account.move']
        return Move.browse(self.env.context['active_ids']).button_validate()
