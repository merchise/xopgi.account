#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# operations_performance_report.py
# ---------------------------------------------------------------------
# Copyright (c) 2015, 2016 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 21/11/15

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)
from openerp import tools
from openerp import fields, models


class OperationPerformanceReport(models.Model):
    _name = "xopgi_operations_performance.opperf_report"
    _description = "Operation Performance Statistics"
    _auto = False

    lead_id = fields.Many2one("crm.lead", "Opportunity")
    lead_month = fields.Selection([
        (1, "January"),
        (2, "February"),
        (3, "March"),
        (4, "April"),
        (5, "May"),
        (6, "June"),
        (7, "July"),
        (8, "August"),
        (9, "September"),
        (10, "October"),
        (11, "November"),
        (12, "December")
    ], "Opportunity Month")
    partner_id = fields.Many2one("res.partner", "Customer")
    manager_id = fields.Many2one("res.users", "Account Manager")
    user_id = fields.Many2one("res.users", string="Salesperson")
    operation_id = fields.Many2one("account.analytic.account", "Operation")
    response_time = fields.Integer(
        "Response Time", group_operator="avg",
        help="Time between opportunity creation and first Quotation")
    proposal_time = fields.Integer(
        "Proposal Time", group_operator="avg",
        help="Time between opportunity creation and first Quotation sent")
    negotiation_time = fields.Integer(
        "Negotiation Time", group_operator="avg",
        help="Time between Quotation sent and first Quotation confirm")
    customer_confirm_time = fields.Integer(
        "Customer Time", group_operator="avg",
        help="Time between opportunity creation and first Quotation confirm")
    invoice_time = fields.Integer(
        "Invoice Time", group_operator="avg",
        help="Time between opportunity creation and first Invoice")

    def init(self, cr):
        tools.drop_view_if_exists(cr,
                                  "xopgi_operations_performance_opperf_report")
        cr.execute(
            """
            CREATE or REPLACE VIEW xopgi_operations_performance_opperf_report AS (
            SELECT
             crm_lead.id,
             crm_lead.id AS lead_id,
             MIN(account_analytic_account.manager_id) AS manager_id,
             crm_lead.partner_id,
             crm_lead.user_id,
             MIN(sale_order.project_id) AS operation_id,
             DATE_PART('month', crm_lead.create_date) AS lead_month,
             CAST(DATE_PART('day', MIN(sale_order.date_order - crm_lead.create_date)) AS INTEGER) AS response_time,
             CAST(DATE_PART('day', MIN(sale_order.send_date - crm_lead.create_date)) AS INTEGER) AS proposal_time,
             CAST(DATE_PART('day', MIN(sale_order.date_confirm - sale_order.send_date)) AS INTEGER) AS negotiation_time,
             CAST(DATE_PART('day', MIN(sale_order.date_confirm - crm_lead.create_date)) AS INTEGER) AS customer_confirm_time,
             CAST(DATE_PART('day', MIN(account_invoice.date_invoice - crm_lead.create_date)) AS INTEGER) AS invoice_time
            FROM
             public.crm_lead
            INNER JOIN
             public.sale_order
            ON
             sale_order.origin = 'Opportunity: ' || crm_lead.id
            OR
             sale_order.origin = 'Oportunidad: ' || crm_lead.id
            OR
             sale_order.origin = 'Opportunité : ' || crm_lead.id
            LEFT OUTER JOIN
             public.account_invoice
            ON
             account_invoice.origin = sale_order.name
            LEFT OUTER JOIN
             public.account_analytic_account
            ON
             sale_order.project_id = account_analytic_account.id
            GROUP BY
             crm_lead.id
            ORDER BY
             crm_lead.id DESC)
             """)


class OperationResultReport(models.Model):
    _name = "xopgi_operations_performance.opresult_report"
    _description = "Operations Results Statistics"
    _auto = False

    analytic_id = fields.Many2one("account.analytic.account",
                                  "Operation")
    code = fields.Char("Reference")
    partner_id = fields.Many2one("res.partner", "Customer")
    manager_id = fields.Many2one("res.users", "Account Manager")
    primary_salesperson_id = fields.Many2one("res.users", string="Salesperson")
    parent_analityc_id = fields.Many2one("account.analytic.account",
                                         "Parent Operation")
    debit = fields.Float("Debit")
    credit = fields.Float("Credit")
    balance = fields.Float("Balance")
    margin_percentage = fields.Float("Margin %", group_operator='avg')
    pax = fields.Integer("Nro. Pax")
    margin_by_pax = fields.Float("Margin by Pax", group_operator='avg')
    date = fields.Date("Expiration Date")
    state = fields.Selection(
        [('template', 'Template'),
         ('draft', 'New'),
         ('open', 'In Progress'),
         ('pending', 'To Renew'),
         ('close', 'Closed'),
         ('cancelled', 'Cancelled')],
        "Status")

    def init(self, cr):
        tools.drop_view_if_exists(cr,
                                  "xopgi_operations_performance_opresult_report")
        cr.execute(
            """
            CREATE or REPLACE VIEW xopgi_operations_performance_opresult_report AS (
            SELECT
              x.id,
              x.id AS analytic_id,
              x.name,
              x.code,
              x.partner_id,
              x.manager_id,
              x.primary_salesperson_id,
              x.parent_id AS parent_analityc_id,
              x.debit,
              x.credit,
              x.balance,
              (CASE WHEN
                 x.debit = 0
               THEN 0
               ELSE
                 x.balance*100/x.debit
               END) AS margin_percentage,
              x.pax,
              (CASE WHEN
                 x.pax = 0
               THEN 0
               ELSE
                 x.balance/x.pax
               END) AS margin_by_pax,
              x.date,
              x.state
            FROM
              (SELECT
              a.id,
              a.name,
              a.code,
              a.partner_id,
              a.manager_id,
              a.primary_salesperson_id,
              a.parent_id,
              a.date,
              a.pax,
              a.state,
              SUM(
                CASE WHEN l.amount > 0
                THEN l.amount
                ELSE 0.0
                END
              ) AS debit,
              SUM(
                CASE WHEN l.amount < 0
                THEN -l.amount
                ELSE 0.0
                END
              ) AS credit,
              COALESCE(SUM(l.amount),0) AS balance
              FROM
                account_analytic_account a
              LEFT JOIN
                account_analytic_line l ON (a.id = l.account_id)
              WHERE
                a.type = 'contract'
              GROUP BY
                a.id) AS x order by x.id desc)
             """)


class CoordinationPerformanceReport(models.Model):
    _name = "xopgi_operations_performance.coordperf_report"
    _description = "Coordination Performance Statistics"
    _auto = False

    purchase_order_id = fields.Many2one("purchase.order", "Purchase Order")
    user_id = fields.Many2one("res.users", "Responsible")
    partner_id = fields.Many2one("res.partner", "Supplier")
    account_analytic_id = fields.Many2one("account.analytic.account",
                                          "Dossier")
    manager_id = fields.Many2one("res.users", "Account Manager")
    planification_time = fields.Integer(
        "Planification Time", group_operator="avg",
        help="Time between call for bids creation and first proccessing")
    reserve_send_time = fields.Integer(
        "Reserve Send Time", group_operator="avg",
        help="Time between PO creation and PO send")
    supplier_response_time = fields.Integer(
        "Supplier Response Time", group_operator="avg",
        help="Time between PO send and PO bid received")
    purchase_time = fields.Integer(
        "Purchase Time", group_operator="avg",
        help="Time between PO creation and confirmation")

    def init(self, cr):
        tools.drop_view_if_exists(cr,
                                  "xopgi_operations_performance_coordperf_report")
        cr.execute(
            """
            CREATE or REPLACE VIEW xopgi_operations_performance_coordperf_report AS (
            SELECT
              purchase_order.id,
              purchase_order.id AS purchase_order_id,
              purchase_requisition.user_id,
              purchase_order.partner_id,
              purchase_requisition.account_analytic_id,
              account_analytic_account.manager_id,
              CAST(DATE_PART('day', purchase_requisition.call_date - purchase_requisition.create_date) AS INTEGER) AS planification_time,
              CAST(DATE_PART('day', purchase_order.send_date - purchase_order.create_date) AS INTEGER) AS reserve_send_time,
              CAST(DATE_PART('day', purchase_order.bid_date - purchase_order.send_date) AS INTEGER) AS supplier_response_time,
              CAST(DATE_PART('day', purchase_order.date_approve - purchase_order.create_date) AS INTEGER) AS purchase_time
            FROM
              public.purchase_order
            LEFT OUTER JOIN
              public.purchase_requisition
            ON
              purchase_order.requisition_id = purchase_requisition.id
            LEFT OUTER JOIN
              public.account_analytic_account
            ON
              purchase_requisition.account_analytic_id = account_analytic_account.id
            WHERE
              purchase_order.state <> 'cancel'
            ORDER BY
              id DESC)
             """)
