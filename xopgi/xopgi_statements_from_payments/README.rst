=====================================
 Create bank statement from payments
=====================================

Allows to create a new Bank/Cash Statement from Payments and/or Journal
Entries.

Select the (unreconciled) payments and in the Action menu, press
'Create Statement'.  This will:

#. Create a new statement in the same journal of the Payments (all payments
   must belong to the same journal);

#. For each, payment creates a line (payments with 0 are ignored) in the
   statement and conciliate the statement line with that that of the payment.


Limitations
===========

- We don't create multi-currency statement lines.

  .. note:: I haven't witnessed any DB where there are statement lines with
            `currency_id` not NULL.
