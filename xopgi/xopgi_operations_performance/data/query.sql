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
 crm_lead.id DESC

SELECT
  x.id,
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
    a.id) AS x order by x.id desc