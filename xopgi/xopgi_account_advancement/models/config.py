#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
from __future__ import division, print_function, absolute_import

from xoeuf import api, fields, models
from xoeuf.odoo.tools.safe_eval import safe_eval
from xoutil.future.collections import opendict


DEFAULT_ACCOUNT_TYPES = {
    'advanced_receivable_type_id': 'advanced_receivable',
    'advanced_payable_type_id': 'advanced_payable'
}

DEFAULT_ADVANCED_JOURNAL_TYPES = {
    'precollection_journal_type_id': 'precollection_type',
    'prepayment_journal_type_id': 'prepayment_type'
}

REGULAR_ACCOUNT_DOMAIN = [
    ('deprecated', '=', False)
]


class Partner(models.Model):
    _inherit = 'res.partner'

    property_account_payment_advance_id = fields.Many2one(
        'account.account',
        company_dependent=True,
        string="Pre-payment Account",
        domain=REGULAR_ACCOUNT_DOMAIN,
        help=("This account will be used instead of the default one as the"
              "payment advance account for the current partner"),
        required=True
    )

    property_account_receivable_advance_id = fields.Many2one(
        'account.account',
        company_dependent=True,
        string="Pre-collection Account",
        domain=REGULAR_ACCOUNT_DOMAIN,
        help=("This account will be used instead of the default one as the"
              "receivable advance account for the current partner"),
        required=True
    )


class XopgiAccountAdvancementConfig(models.AbstractModel):
    _name = 'xopgi.account_adv.config.settings'

    @api.multi
    def get_account_types(self):
        '''Returns a dictionary of type opendict() with the system params:
        advanced_receivable_type_id and advanced_payable_type_id and their
        values.

        '''
        res = opendict()
        get_param = self.env['ir.config_parameter'].get_param
        for param in DEFAULT_ACCOUNT_TYPES:
            value = safe_eval(str(get_param(param))) or False
            res[param] = value
            if self:
                setattr(self, param, value)
        return res

    @api.one
    def _set_account_types(self):
        '''Set the account types Receivable Advanced when fields
        advanced_receivable_type_id or advanced_payable_type_id change and
        update the filter in account settings with the new field values.

        '''
        set_param = self.env['ir.config_parameter'].set_param
        for param in DEFAULT_ACCOUNT_TYPES:
            set_param(param, repr(getattr(self, param).id))

    @api.multi
    def get_advanced_journal_types(self):
        '''Returns a dictionary of type opendict() with the system params:
        and their precollection_journal_type_id and prepayment_journal_type_id
        values.

        '''
        res = opendict()
        get_param = self.env['ir.config_parameter'].get_param
        for param in DEFAULT_ADVANCED_JOURNAL_TYPES:
            value = safe_eval(str(get_param(param))) or False
            res[param] = value
            if self:
                setattr(self, param, value)
        return res

    @api.one
    def _set_advanced_journal_types(self):
        '''Set the advance journal types when fields
        precollection_journal_type_id or prepayment_journal_type_id change and
        update the filter in account settings with the new field values.

        '''
        set_param = self.env['ir.config_parameter'].set_param
        for param in DEFAULT_ADVANCED_JOURNAL_TYPES:
            set_param(param, repr(getattr(self, param).id))

    advanced_receivable_type_id = fields.Many2one(
        'account.account.type',
        compute='get_account_types',
        inverse='_set_account_types',
        default=lambda self: self.get_account_types().advanced_receivable_type_id,
        help='The type of pre-collection accounts.',
    )

    advanced_payable_type_id = fields.Many2one(
        'account.account.type',
        compute='get_account_types',
        inverse='_set_account_types',
        default=lambda self: self.get_account_types().advanced_payable_type_id,
        help='The type of the pre-payment accounts.',
    )

    precollection_journal_type_id = fields.Many2one(
        'account.journal',
        compute='get_advanced_journal_types',
        inverse='_set_advanced_journal_types',
        default=lambda self: self.get_advanced_journal_types().precollection_journal_type_id,
        help='The type of journal for pre-collection accounts',
    )

    prepayment_journal_type_id = fields.Many2one(
        'account.journal',
        compute='get_advanced_journal_types',
        inverse='_set_advanced_journal_types',
        default=lambda self: self.get_advanced_journal_types().prepayment_journal_type_id,
        help='The type of journal for pre-payment accounts',
    )


class Config(models.TransientModel):
    _name = 'account.config.settings'
    _inherit = [_name, XopgiAccountAdvancementConfig._name]


def get_account_config(self):
    config = self.env['account.config.settings'].search([], limit=1)
    if not config:
        config = self.env['account.config.settings'].create({})
    return config
