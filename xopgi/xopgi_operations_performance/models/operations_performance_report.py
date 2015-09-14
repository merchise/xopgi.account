# -*- coding: utf-8 -*-

from openerp import tools
from openerp import fields, models


class OperationPerformanceReport(models.Model):
    _name = "xopgi_operations_performance.opperf_report"
    _description = "Operation Performance Statistics"
    _auto = False

    lead_id = fields.Many2one("crm.lead", "Opportunity")
    response_time = fields.Integer(
        "Response Time",
        help="Time between opportunity creation and first Quotation")
    proposal_time = fields.Integer(
        "Proposal Time",
        help="Time between opportunity creation and first Quotation sent")
    negotiation_time = fields.Integer(
        "Negotiation Time",
        help="Time between Quotation sent and first Quotation confirm")
    customer_confirm_time = fields.Integer(
        "Customer Time",
        help="Time between opportunity creation and first Quotation confirm")
    invoice_time = fields.Integer(
        "Invoice Time",
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
    debit = fields.Float("Debit")
    credit = fields.Float("Credit")
    balance = fields.Float("Balance")
    margin_percentage = fields.Float("Margin %")
    pax = fields.Integer("Nro. Pax")
    margin_by_pax = fields.Float("Margin by Pax")
    date = fields.Date("Expiration Date")

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
              x.date
            FROM
              (SELECT
              a.id,
              a.name,
              a.code,
              a.date,
              a.pax,
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
    planification_time = fields.Integer(
        "Planification Time",
        help="Time between call for bids creation and first proccessing")
    reserve_send_time = fields.Integer(
        "Reserve Send Time",
        help="Time between PO creation and PO send")
    supplier_response_time = fields.Integer(
        "Supplier Response Time",
        help="Time between PO send and PO bid received")
    purchase_time = fields.Integer(
        "Purchase Time",
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
            WHERE
              purchase_order.state <> 'cancel'
            ORDER BY
              id DESC)
             """)
