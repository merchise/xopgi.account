# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi.xopgi.xopgi_account.move
# ---------------------------------------------------------------------
# Copyright (c) 2013-2015 Merchise Autrement
# All rights reserved.
#
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# @created: 2013-11-30

'''Extensions & fixes for account move lines.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _absolute_import)

from openerp.osv import fields
from openerp.osv.orm import Model, TransientModel
import openerp.addons.decimal_precision as dp
import openerp.addons.account.wizard.account_fiscalyear_close \
    as base_fiscalyear_close

from openerp.addons.account.account import account_move as base_move
import openerp.addons.account.account_move_line as base_move_line

from xoutil.names import nameof

from xoeuf.osv.orm import get_modelname, store_identity


try:
    from xoeuf.osv.orm import guess_id  # migrate
except ImportError:
    def guess_id(which, attr='id'):
        '''Guess the id of an object.

        If `which` is an integer, it is returned unchanged.  If it is a dict
        or a browse_record the attribute/key given by `attr` is look up and
        return.  If not found an AttibuteError is raised.  Any other type is a
        TypeError.

        '''
        from openerp.osv.orm import browse_record
        from xoutil.collections import Mapping
        from six import integer_types
        if isinstance(which, integer_types):
            return which
        elif isinstance(which, (Mapping, browse_record)):
            from xoutil.objects import smart_getter
            get = smart_getter(which, strict=True)
            return get(attr)
        else:
            raise TypeError


def _convert(self, cr, uid, value, date, from_currency, to_currency,
             context=None):
    '''Helper to convert from one currency to another.'''
    from openerp.addons.base.res.res_currency import res_currency
    currency_obj = self.pool[get_modelname(res_currency)]
    context = dict(context or {}, date=date)
    from_currency = guess_id(from_currency)
    to_currency = guess_id(to_currency)
    return currency_obj.compute(cr, uid, from_currency, to_currency,
                                value, context=context)


class account_move(Model):
    '''Fixes to account move.'''
    _name = get_modelname(base_move)
    _inherit = _name

    def onchange_journal(self, cr, uid, ids, journal_id, previous_period_id,
                         date, context=None):
        '''Handles the on_change trigger for the journal.

        It takes care of calculating the domain for the period_id and it's
        value.  Also if the currently selected period does not comply with
        it's new domain, it defaults to the period that matches `date` for the
        newly selected journal's company.

        Finally the `company_id` is re-calculated.

        '''
        from openerp.addons.account.account import account_period
        from openerp.addons.account.account import account_journal
        from xoeuf.osv.model_extensions import field_value
        result = {}
        if journal_id:
            journal_obj = self.pool[get_modelname(account_journal)]
            company_id = field_value(journal_obj, cr, uid, journal_id,
                                     'company_id', context=context)
            values = result.setdefault('value', {})
            domains = result.setdefault('domain', {})
            domains['period_id'] = [('company_id', '=', company_id)]
            if previous_period_id:
                period_obj = self.pool[get_modelname(account_period)]
                previous_period = period_obj.browse(
                    cr, uid, previous_period_id, context=context)
                if previous_period.company_id.id != company_id:
                    context = dict(context, company_id=company_id)
                    period_id = period_obj.find(cr, uid, date,
                                                context=context)
                    if isinstance(period_id, list):
                        period_id = period_id[0]
                    values['period_id'] = period_id
            values['company_id'] = company_id
        return result


class account_move_line(Model):
    '''Fixes to account move lines.

    '''
    _name = get_modelname(base_move_line.account_move_line)
    _inherit = _name

    def _query_get(self, cr, uid, obj='l', context=None):
        """Builds the QUERY for selecting the journal items for the chart of
        accounts.

        This method modifies the query for the case of the `Consolidated
        Holding`, in which case:

        a) Journal entries for which the partner belongs to the holding.

        .. warning:: About holding and companies.

           - This method works for a single holding in the data base.

           - The holding is the company that does not have a parent.

        """
        # TODO: Support multi-holding.
        res = super(account_move_line, self)._query_get(cr, uid, obj, context)
        if context.get('consolidate', False):
            to_search = [
                ('company_id', '!=', False),
                ('company_id.parent_id', '!=', False)
            ]
            partner = self.pool.get('res.partner')
            partner_ids = partner.search(cr, uid, to_search, context=context)
            res += "AND partner_id NOT IN " + str(tuple(partner_ids))
        return res

    def _get_currency_credit_debit(self, cr, uid, ids, fields, arg,
                                   context=None):
        '''Functional getter for `credit` and `debit` fields.

        This changes the normal behaviour of a single :class:`journal item
        <account_move_line>`. Instead of having a separate `amount_currency`
        field when the currency is not the same as the one defined for
        company, use debit for positive `amount_currency` and credit for
        negative.

        '''
        from xoutil.types import is_collection
        if not is_collection(fields):
            fields = [fields, ]
        result = {}
        for obj in self.browse(cr, uid, ids, context):
            if obj:
                result[obj.id] = {}
                for field_name in fields:
                    result[obj.id][field_name] = 0
                    # Notice: currency_debit should only have a value if the value
                    # is bigger than 0, and currency_credit should only have a
                    # value if it's less that 0. Otherwise they'll always get the
                    # same value, and only ONE of them should have a value, that's
                    # why we need the conditions.
                    if obj.currency_id:
                        value = obj.amount_currency
                        if field_name == 'currency_debit' and value > 0:
                            result[obj.id][field_name] = value
                        elif field_name == 'currency_credit' and value < 0:
                            result[obj.id][field_name] = abs(value)
                    else:
                        true_field = field_name.split('_')[-1]
                        result[obj.id][field_name] = getattr(obj, true_field)
        return result

    def _set_currency_credit_debit(self, cr, uid, line_id, name, value, arg,
                                   context=None, _update_check=True):
        '''The setter for the `currency_credit` and `currency_debit` fields.

        See :meth:`_get_currency_credit_debit`.

        :param arg: The original field name.

        '''
        move_line = self.browse(cr, uid, line_id, context=context)
        if move_line:
            # Be safe. Fixes bug when creating several lines.  I think this
            # has to do with a (JS?)  computation of credit/debit for lines
            # based on current lines.  Not sure.
            to_write = dict(debit=0, credit=0)
            if value != 0:
                if move_line.currency_id:
                    from_currency = move_line.currency_id.id
                    to_currency = move_line.account_id.company_id.currency_id.id
                    base_value = _convert(self, cr, uid, value, move_line.date,
                                          from_currency, to_currency,
                                          context=context)
                    to_write[arg] = base_value
                    if name == 'currency_debit':
                        to_write['amount_currency'] = value
                    elif name == 'currency_credit':
                        to_write['amount_currency'] = -value
                else:
                    to_write[arg] = value
                    to_write['amount_currency'] = 0  # Otherwise a validation
                                                     # error might hunt you
                return self.write(cr, uid, line_id, to_write, context,
                                  update_check=_update_check)

    def recalculate(self, cr, uid, ids, account_id,
                    debit, credit, currency,
                    context=None):
        '''Event handler that recalculates debit and credit in the company's
        base currency.

        '''
        from datetime import datetime
        from xoeuf.tools import normalize_datetime
        from openerp.addons.account.account import account_account
        account_obj = self.pool[get_modelname(account_account)]
        if account_id:
            account = account_obj.browse(cr, uid, account_id, context=context)
            company_currency = account.company_id.currency_id.id
            move_date = context.get('parent_date', datetime.now())
            move_date = normalize_datetime(move_date)
            values = dict(credit=_convert(self, cr, uid, credit, move_date,
                                          currency, company_currency),
                          debit=_convert(self, cr, uid, debit, move_date,
                                         currency, company_currency))
            return dict(value=values)
        else:
            # If no journal is selected account_id is False, so change
            # nothing.
            return {}

    _CURRENCY_INVALIDATE_RULE = {
        _name: (store_identity,
                ['credit', 'debit', 'amount_currency', 'currency_id'],
                10)
    }

    _columns = {
        'currency_debit':
            fields.function(_get_currency_credit_debit,
                            type='float', store=_CURRENCY_INVALIDATE_RULE,
                            arg='debit', fnct_inv_arg='debit',
                            fnct_inv=_set_currency_credit_debit,
                            digits_compute=dp.get_precision('Account'),
                            string='Debit',
                            multi=nameof(_get_currency_credit_debit)),
        'currency_credit':
            fields.function(_get_currency_credit_debit,
                            type='float', store=_CURRENCY_INVALIDATE_RULE,
                            arg='credit', fnct_inv_arg='credit',
                            fnct_inv=_set_currency_credit_debit,
                            digits_compute=dp.get_precision('Account'),
                            string='Credit',
                            multi=nameof(_get_currency_credit_debit))
    }


UPDATE_SQL_TEMPLATE = '''
UPDATE account_move_line
SET currency_debit = (
      CASE WHEN currency_id IS NOT NULL AND amount_currency > 0
           THEN amount_currency
           ELSE debit
      END),
    currency_credit = (
      CASE WHEN currency_id IS NOT NULL AND amount_currency < 0
           THEN -amount_currency
           ELSE credit
      END)
WHERE id={id};
'''


# Since the closing entry is made by magical SQL, we need to invoke the
# computation of functional fields by ourselves.
class account_fiscalyear_close(TransientModel):
    '''Recalculates functional fields for the generated closing entry.'''
    _name = get_modelname(base_fiscalyear_close.account_fiscalyear_close)
    _inherit = _name

    def data_save(self, cr, uid, ids, context=None):
        # The super implementation is filled with SQL, our approach is to
        # simply emit UPDATEs afterwards.  Doing via the ORM is a resource
        # hog.
        from xoeuf.osv import savepoint
        from xoeuf.osv.model_extensions import search_browse
        _super = super(account_fiscalyear_close, self).data_save
        with savepoint(cr, 'xopgi_fy_close_data_save'):
            _super(cr, uid, ids, context=context)
        move_obj = self.pool['account.move']
        data = self.browse(cr, uid, ids, context=context)[0]
        journal_id = data.journal_id.id
        period_id = data.period_id.id
        query = [('journal_id', '=', journal_id),
                 ('period_id', '=', period_id)]
        move = search_browse(move_obj, cr, uid, query, context=context)
        sentences = []
        for line in move.line_id:
            sentences.append(UPDATE_SQL_TEMPLATE.format(id=line.id))
        if sentences:
            cr.execute(''.join(sentences))
        return {
            # Go to the view of the generated entry.
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'account.move',
            'res_id': move.id,
        }
