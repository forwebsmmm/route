# -*- coding: utf-8 -*-
# Copyright (C) 2016-TODAY touch:n:track <https://tnt.pythonanywhere.com>
# Part of tnt: Router addon for Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class TntRouter(models.Model):
    _name = 'tnt.router'
    _description = 'Tnt Router'

    name = fields.Char(string='Route name')
    from_customer = fields.Many2one('res.partner', string='From customer',
                                    default=lambda self: self.env.user.commercial_partner_id.id,
                                    domain="[('is_company','=',1)]")
    customers = fields.Many2many('res.partner', string='Customers',  domain="[('customer','=',1), ('parent_id','=',False)]")
    sequence_ids = fields.One2many('tnt.router.sequence', 'route', 'Sequences')
    points_ids = fields.One2many('tnt.router.point', 'route', 'Points')
    transport_type = fields.Selection([
        ('driving-car', 'Car'),
        ('driving-hgv', 'Heavy Vehicle'),
        ('foot-walking', 'Walking'),
        ('foot-hiking', 'Hiking'),
        ('cycling-regular', 'Bicycle'),
        ('cycling-road', 'Road bike'),
        ('cycling-mountain', 'Mountain bike '),
        ('cycling-electric', 'E-bike'),
    ], string='Type', default='driving-car')

    @api.multi
    def generate_route(self):
        return True


class TntRouterPoint(models.Model):
    _name = 'tnt.router.point'
    _description = 'Tnt Router Point'

    route = fields.Many2one('tnt.router', string='Route')
    sequence = fields.Integer(string='Sequence')
    latitude = fields.Float(string='Latitude', digits=(16, 5))
    longitude = fields.Float(string='Longitude', digits=(16, 5))

class TntRouterSequence(models.Model):
    _name = 'tnt.router.sequence'
    _description = 'Tnt Router Sequence'
    _order = 'sequence'

    route = fields.Many2one('tnt.router', string='Route')
    sequence = fields.Integer(string='Sequence')
    customer = fields.Many2one('res.partner', string='Route')
    latitude = fields.Float(string='Latitude', digits=(16, 5))
    longitude = fields.Float(string='Longitude', digits=(16, 5))