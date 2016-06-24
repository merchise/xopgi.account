# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi.xopgi.xopgi_account.journal
# ---------------------------------------------------------------------
# Copyright (c) 2013-2016 Merchise Autrement [~º/~]
# All rights reserved.
#
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# @created: 2013-12-27


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _absolute_import)

from openerp.models import Model
from openerp.api import guess

from openerp.release import version_info as ODOO_VERSION_INFO


def _get_initials(name):
    return ''.join(word[0].upper() for word in name.split())


class MultiCompanyItem(object):
    '''Mixin for models that are involved in multicompany scenarios.

    Fixes names (that could be equal) to have the company's initial.

    .. important:: You should place this class *before* Model.

    '''
    @guess
    def name_get(self, cr, uid, ids, context=None):
        '''Adds the Company's Initial to each journal name.

        '''
        companies = self.pool['res.company']
        hasmany_companies = len(companies.search(cr, uid, [])) > 1
        if not ids:
            return []
        if isinstance(ids, (int, long)):
            ids = [ids]
        rows = self.read(cr, uid, ids, ['name', 'company_id'],
                         context=context)
        res = []
        for row in rows:
            name = row['name']
            if hasmany_companies:
                company = _get_initials(row['company_id'][1])
                if company:
                    name += ' - %s' % company
            res.append((row['id'], name))
        return res


class account_journal(MultiCompanyItem, Model):
    _inherit = 'account.journal'


if ODOO_VERSION_INFO < (9, 0):
    # Odoo 9 does not have the fiscal year and period objects.  Instead
    # company's have fiscal year's closure (lock) dates.
    class account_fiscalyear(MultiCompanyItem, Model):
        _inherit = 'account.fiscalyear'

    class account_period(MultiCompanyItem, Model):
        _name = 'account.period'
        _inherit = _name
