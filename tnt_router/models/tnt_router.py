# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TntRouter(models.Model):
    _name = 'tnt.router'
    _description = 'Tnt Router'

    name = fields.Char(string='Route name')
    from_customer = fields.Many2one('res.partner', string='From customer',
                                    default=lambda self: self.env.user.commercial_partner_id.id,
                                    domain="[('is_company','=',1)]")
    customers = fields.Many2many('res.partner', string='Customers',  domain="[('customer','=',1), ('parent_id','=',False)]")

    @api.multi
    def route_generator(self):
        return True


class TntRoutePoint(models.Model):
    _name = 'tnt.route.point'
    _description = 'Tnt Route Point'

    route = fields.Many2one('tnt.router', string='Route')
    sequence = fields.Integer(string='Sequence')
    latitude = fields.Float(string='Latitude', digits=(16, 5))
    longitude = fields.Float(string='Longitude', digits=(16, 5))
