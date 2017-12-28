#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

import json
from xoeuf import MAJOR_ODOO_VERSION
from xoeuf.odoo.tests.common import HttpCase


if MAJOR_ODOO_VERSION < 11:
    import urllib2

    class JSONRequestMaker(urllib2.HTTPHandler):
        def http_request(self, request):
            request = urllib2.HTTPHandler.http_request(self, request)
            request.add_unredirected_header(
                'Content-type',
                'application/json'
            )
            return request

    def setup_json(self):
        self.opener.add_handler(JSONRequestMaker())

else:
    def setup_json(self):
        self.opener.headers['Content-Type'] = 'application/json'


class TestVoucherOnchangeRegression(HttpCase):
    '''Regression test for issue `MERCURIO-1MA`__.

    __ https://sentry.lahavane.com/caraibes/mercurio/issues/5892/


    '''
    post_install = True
    at_install = not post_install

    if MAJOR_ODOO_VERSION < 11:
        @staticmethod
        def getcode(response):
            return response.getcode()

        @staticmethod
        def get_payload(response):
            return json.loads(response.read())

    else:
        @staticmethod
        def getcode(response):
            # Odoo 11+ uses requests to load the URL.
            return response.status_code

        @staticmethod
        def get_payload(response):
            return response.json()

    def test_onchange_company_without_arguments(self):
        self.authenticate('admin', 'admin')
        setup_json(self)
        response = self.url_open(
            '/web/dataset/call_kw/account.voucher/onchange',
            json.dumps({
                "params": {
                    "model": "account.voucher",
                    "args": [
                        [],
                        {"company_id": self.env.ref('base.main_company').id,
                         "id": False},
                        ["company_id"],
                        {"company_id": "onchange_company()"}
                    ],
                    "method": "onchange",
                    "kwargs": {}},

                "jsonrpc": "2.0",
                "id": id(self),
                "method": "call"})
        )
        # Well Odoo, does return 200 (even for a TypeError as described in
        # MERCURIO-1MA), but the payload says it's an error.  So I have to
        # assume a *good* response of error.
        self.assertEqual(200, self.getcode(response))
        payload = self.get_payload(response)
        self.assertNotIn('error', payload)

    def test_onchange_company_with_many_args(self):
        self.authenticate('admin', 'admin')
        setup_json(self)
        response = self.url_open(
            '/web/dataset/call_kw/account.voucher/onchange',
            json.dumps({
                "params": {
                    "model": "account.voucher",
                    "args": [
                        [],
                        {"company_id": self.env.ref('base.main_company').id,
                         "id": False},
                        ["company_id"],
                        {"company_id": "onchange_company(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)"}
                    ],
                    "method": "onchange",
                    "kwargs": {}},

                "jsonrpc": "2.0",
                "id": id(self),
                "method": "call"})
        )
        # Well Odoo, does return 200 (even for a TypeError as described in
        # MERCURIO-1MA), but the payload says it's an error.  So I have to
        # assume a *good* response of error.
        self.assertEqual(200, self.getcode(response))
        payload = self.get_payload(response)
        self.assertNotIn('error', payload)
