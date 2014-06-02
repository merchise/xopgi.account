# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# xopgi.xopgi.xopgi_account.journal
#----------------------------------------------------------------------
# Copyright (c) 2013, 2014 Merchise Autrement
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
                        unicode_literals as _py3_unicode,
                        absolute_import as _absolute_import)

from openerp.osv.orm import Model
import openerp.addons.account.account as base_account

from xoeuf.osv.orm import get_modelname


def _get_initials(name):
    return ''.join(word[0].upper() for word in name.split())


class MultiCompanyItem(object):
    '''Mixin for models that are involved in multicompany scenarios.

    Fixes names (that could be equal) to have the company's initial.

    .. important:: You should place this class *before* Model.

    '''
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
    _name = get_modelname(base_account.account_journal)
    _inherit = _name


class account_fiscalyear(MultiCompanyItem, Model):
    _name = get_modelname(base_account.account_fiscalyear)
    _inherit = _name


class account_period(MultiCompanyItem, Model):
    _name = get_modelname(base_account.account_period)
    _inherit = _name
