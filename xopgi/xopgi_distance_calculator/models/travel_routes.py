# -*- coding: utf-8 -*-
from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from openerp import fields, models


class RoutePoints(models.Model):
    _name = "res.route.points"
    _order = 'name'

    name = fields.Char(string="Route Point", required=True)
    state_id = fields.Many2one(comodel_name="res.country.state", ondelete='restrict', required=True)
    is_state_reference = fields.Boolean(default=False)
    origin_point_id = fields.One2many(comodel_name="res.routes", inverse_name='origin_point_id')
    destination_point_id = fields.One2many(comodel_name="res.routes", inverse_name='destination_point_id')


class Routes(models.Model):
    _name = "res.routes"

    origin_point_id = fields.Many2one(comodel_name="res.route.points", ondelete='restrict', required=True)
    destination_point_id = fields.Many2one(comodel_name="res.route.points", ondelete='restrict', required=True)
    distance = fields.Float()
