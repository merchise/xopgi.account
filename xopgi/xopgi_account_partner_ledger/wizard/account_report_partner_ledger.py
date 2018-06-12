#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoutil.context import Context
from xoeuf import fields, models, api

# This context use to hack the `query_get` function in the ` Account Partner
# Ledger` report to filter the data of the report by partners.
PARTNER_LEDGER_CONTEXT = object()


class AccountPartnerLedger(models.TransientModel):
    _inherit = "account.report.partner.ledger"

    partner_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Partners'
    )

    def _print_report(self, data):
        if self.partner_ids:
            data['form'].update(partner_ids=self.partner_ids.ids)
        return super(AccountPartnerLedger, self)._print_report(data)


class ReportPartnerLedger(models.AbstractModel):
    _inherit = 'report.account.report_partnerledger'

    @api.model
    def render_html(self, docids, data=None):
        partner_ids = data['form'].get('partner_ids', [])
        with Context(PARTNER_LEDGER_CONTEXT, partners_filter=partner_ids):
            return super(ReportPartnerLedger, self).render_html(docids, data)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def _query_get(self, domain=None):
        # Add condition to the where clause with the filter by partners in the
        # context of the `Account Partner Ledger` report.
        tables, where_clause, where_clause_params = super(AccountMoveLine, self)._query_get(domain)
        if PARTNER_LEDGER_CONTEXT in Context:
            partner_ids = Context[PARTNER_LEDGER_CONTEXT].get('partners_filter', False)
            if partner_ids:
                clause = ' AND "account_move_line".partner_id IN (%s)'
                separator = ','
                where_clause += clause % separator.join(str(p) for p in partner_ids)
        return tables, where_clause, where_clause_params
