# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi.xopgi.xopgi_account.move
# ---------------------------------------------------------------------
# Copyright (c) 2013-2017 Merchise Autrement [~º/~]
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
from xoeuf.osv.orm import guess_id


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
    _name = this = get_modelname(base_move_line.account_move_line)
    _inherit = _name

    def default_get(self, cr, uid, fields, context=None):
        '''Gets the defaults for debit and credit in proper currency.

        The UI injects the lines in the `context['line_id']`.  We take the
        first currency to compute the remaining debit/credit balance and
        propose a balancing item.

        If the same entry has several currencies then this won't work very
        well, but it is expected that be a rare case.

        .. note:: We don't trying to recompute the debit and credit in base
           currency since the UI will trigger an onchange to that with the
           `recalculate`:meth: method.

        .. warning:: We assume both `currency_debit` and `currency_credit` are
           to be returned.

        '''
        try:
            from xoutil.symbols import Unset
        except ImportError:
            from xoutil import Unset
        from xoutil.eight import integer_types
        result = super(account_move_line, self).default_get(
            cr, uid, fields, context=context
        )
        default_currency = result.get('currency_id', None)
        entry_currency = default_currency if default_currency else Unset
        balance = curr_debit = curr_credit = 0
        move_obj = self.pool['account.move']
        if context.get('line_id'):
            lines = move_obj.resolve_2many_commands(cr, uid, 'line_id',
                                                    context.get('line_id'),
                                                    context=context)
            for line in lines:
                currency_id = line.get('currency_id', None)
                if not isinstance(currency_id, integer_types):
                    # XXX: Sometimes is (id, name) and other is id alone.
                    currency_id = currency_id[0]
                if entry_currency is Unset:
                    entry_currency = currency_id
                if entry_currency == currency_id:
                    curr_debit += line.get('currency_debit', 0)
                    curr_credit += line.get('currency_credit', 0)
            balance = curr_debit - curr_credit
        result.update(
            currency_debit=-balance if balance < 0 else 0,
            currency_credit=balance if balance > 0 else 0,
            currency_id=entry_currency if entry_currency else default_currency
        )
        return result

    def _calc_currency_debit_credit(self, obj, fields=None):
        try:
            from xoutil.future.collections import opendict
        except ImportError:
            from xoutil.collections import opendict
        if not fields:
            fields = ('currency_debit', 'currency_credit')
        result = opendict.fromkeys(fields, 0)
        # default_get is called to restore missing defaults.  In this case the
        # currency_id may be unset, and we default to do nothing.
        if getattr(obj, 'currency_id', None):
            value = obj.amount_currency
            # Notice: currency_debit should only have a value if the value is
            # bigger than 0, and currency_credit should only have a value if
            # it's less that 0. Otherwise they'll always get the same value,
            # and only ONE of them should have a value, that's why we need the
            # conditions.
            if value > 0:
                result['currency_debit'] = value
            else:
                result['currency_credit'] = -value
            result['line_amount_currency'] = value
        else:
            result['line_amount_currency'] = obj.debit - obj.credit
        return result

    def _get_currency_credit_debit(self, cr, uid, ids, fields, arg,
                                   context=None):
        '''Functional getter for `credit` and `debit` fields.

        This changes the normal behaviour of a single :class:`journal item
        <account_move_line>`: Instead of having a separate `amount_currency`
        field when the currency is not the same as the one defined for
        company, use debit for positive `amount_currency` and credit for
        negative.

        '''
        from xoutil.types import is_collection
        if not is_collection(fields):
            fields = [fields, ]
        result = {}
        for line in self.browse(cr, uid, ids, context=context):
            if line:
                result[line.id] = {}
                res = self._calc_currency_debit_credit(line, fields)
                for field_name in fields:
                    result[line.id][field_name] = res.get(field_name, 0)
                    if not line.currency_id:
                        true_field = self._columns[field_name]._arg
                        result[line.id][field_name] = getattr(line, true_field)
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
                    # Otherwise a validation error might hunt you
                    to_write['amount_currency'] = 0
                return self.write(cr, uid, line_id, to_write, context,
                                  update_check=_update_check)

    def _get_line_currency_amount(self, cr, uid, ids, field, arg,
                                  context=None):
        result = {}
        for line in self.browse(cr, uid, ids, context=context):
            if line.currency_id:
                result[line.id] = line.amount_currency
            else:
                result[line.id] = line.debit - line.credit
        return result

    def _get_line_currency(self, cr, uid, ids, field, arg, context=None):
        result = {}
        for line in self.browse(cr, uid, ids, context=context):
            if line.currency_id:
                result[line.id] = line.currency_id.id
            else:
                result[line.id] = line.company_id.currency_id.id
        return result

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

    # Change whenever either currency, credit, debit or the amount currency
    # change.
    _CURRENCY_INVALIDATE_RULE = {
        this: (
            store_identity,
            ['credit', 'debit', 'amount_currency', 'currency_id'],
            10  # TODO:  Find out what does 10 mean and make it a name const.
        )
    }

    # Change whenever the currency of the line changes.
    _CURRENCY_ONLY_INVALIDATE_RULE = {
        this: (
            store_identity,
            ['currency_id'],
            10
        )
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
                            multi=nameof(_get_currency_credit_debit)),
        'line_currency_amount':
            fields.function(_get_line_currency_amount,
                            type='float',
                            store=_CURRENCY_INVALIDATE_RULE,
                            arg='amount_currency',
                            string='Currency Amount',),
        'line_currency':
            fields.function(_get_line_currency,
                            type='many2one',
                            relation='res.currency',
                            store=_CURRENCY_ONLY_INVALIDATE_RULE,
                            string='Proper currency', ),
    }


# Since the closing entry is made by magical SQL, we need to invoke the
# computation of functional fields by ourselves.

UPDATE_SQL_QUERY = '''
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
      END),
   line_currency_amount = (
      CASE WHEN currency_id IS NOT NULL
          THEN amount_currency
          ELSE debit - credit
      END),
   line_currency = (
      CASE WHEN currency_id IS NOT NULL
          THEN currency_id
          ELSE %s
      END)
WHERE id IN %s;
'''


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
        ids = tuple(line.id for line in move.line_id)
        currency_id = data.journal_id.company_id.currency_id.id
        if ids:
            cr.execute(UPDATE_SQL_QUERY, (currency_id, ids, ))
            # The following is to make sure any cache in the current
            # environment is properly invalidated, since we're modifying the
            # DB via SQL.
            self.invalidate_cache(cr, uid, context=context)
        return {
            # Go to the view of the generated entry.
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'account.move',
            'res_id': move.id,
        }
