============================
 Multi-company for holdings
============================

:author: Manuel Vázquez Acosta <manuel@merchise.org>

This document is an **early draft**, meaning that is contents be inaccurate,
incomplete and thus subject to future changes without notice.

Introduction
============

The purpose of this module is to support accounting tasks for companies
organized as holdings.  We understand a holding as company that owns another
companies and that manage them (at least to the point needed by the holding)
in the instance of Odoo.

If your instance has a single company you won't need this module.


Reporting of consolidated statements
====================================

Both `US GAAP`_ and `IFRS`_ require that when a company invest in another in a
way the investor has controlling power over the investee, the investor must
make *consolidated statements*.

Since holdings by our definition has controlling power of its subsidiaries,
this rule applies.

This module may evolve towards a more elaborate definition of the
relationships between the companies in a single instance, but since
non-controlling investments are unlikely to be managed by the same ERP this is
unlikely.

    Consolidated financial statements show the financial position, results of
    operations, and cash flows of all entities under the parent's control,
    including all subsidiaries.  These statements are prepared as if the
    business were organized as one entity.  The parent uses the equity method
    in its accounts, but the investment account is not reported on the
    parent's financial statements.  Instead, the individual assets and
    liabilities of the parent and its subsidiaries are combined on one balance
    sheet. Their revenues and expenses also are combined on one income
    statement, and their cash flows are combined on one statement of cash
    flows.

    -- [Wild2011]_.

This module allows to produce the statements for a holding automatically by
using the consolidation method, while allowing to do exclusions (marked in the
report) to compare overall performance against parts of the holding.  Also the
Interactive Chart of Accounts allows to show consolidated data.

The consolidation accounts are used for aggregating accounts of the
subsidiaries.


Definitions
===========

.. _GAAP:
.. _US GAAP:

US GAAP

   United States Generally Accepted Accounting Practices.  Includes several
   norms and regulations about how to do proceedings in accounting.

.. _IFRS:

IFRS

   International Financial Reporting Standards.  A set of standards for
   reporting financial statements.  Used broadly in Europe.  The organizations
   and institutions of the United States responsible for the GAAP_ have
   defined a roadmap for standardizing the use of IFRS in the US as well.


Bibliography
============

.. [Wild2011] Fundamental Account Principles, 20th edition. By John J. Wild,
   Ken W. Shaw and Barbara Chiappetta.

   McGraw-Hill/Irwin, 2011.  ISBN-13: 978-0-07-811087-0

   cf. Chapter 15: Investments and International Operations.
