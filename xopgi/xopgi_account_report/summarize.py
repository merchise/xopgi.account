# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi, Guewen Baconnier
#    Copyright Camptocamp SA 2011
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import time

from openerp.osv import fields, orm


class SummarizeAccountPartnerBalanceWizard(orm.TransientModel):

    """Will launch partner balance report and pass required args"""

    _inherit = "account.common.balance.report"
    _name = "partner.balance.webkit"
    #_name = "summarize.partners.balance.webkit"
    _description = "Summarize Partner Balance Report"

    # _columns = {
    #     'amount_currency': fields.boolean("With Currency",
    #                                       help="It adds the currency column"),
    #
    # }


    _columns = {
        'result_selection': fields.selection(
            [('customer', 'Receivable Accounts'),
             ('supplier', 'Payable Accounts'),
             ('customer_supplier', 'Receivable and Payable Accounts')],
            "Partner's", required=True),
        'partner_ids': fields.many2many(
            'res.partner', string='Filter on partner',
            help="Only selected partners will be printed. \
                  Leave empty to print all partners."),
        'amount_currency': fields.boolean("With Currency",
                                          help="It adds the currency column"),
    }

    _defaults = {
        'result_selection': 'customer_supplier',
        'amount_currency' : True,
    }

    def pre_print_report(self, cr, uid, ids, data, context=None):
        data = super(SummarizeAccountPartnerBalanceWizard, self).pre_print_report(
            cr, uid, ids, data, context)
        # if context is None:
        #     context = {}
        # # will be used to attach the report on the main account
        # data['ids'] = [data['form']['chart_account_id']]
        # vals = self.read(cr, uid, ids,
        #                  ['amount_currency'],
        #                  context=context)[0]
        # data['form'].update(vals)


        vals = self.read(cr, uid, ids,
                         ['result_selection', 'partner_ids', 'amount_currency'],
                         context=context)[0]
        data['form'].update(vals)

        return data





    def _print_report(self, cursor, uid, ids, data, context=None):
        # we update form with display account value
        # action = super(SummarizeAccountPartnerBalanceWizard, self)._print_report(cursor, uid, ids, data, context=context)
        # if context and context.get('summarize', False):
        #     action['report_name'] = 'summarize_partner_balance_webkit'
        # return action
          data = self.pre_print_report(cursor, uid, ids, data, context=context)

          return {'type': 'ir.actions.report.xml',
                  'report_name': 'summarize_partner_balance_webkit',
                  'datas': data}

