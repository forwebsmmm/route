# -*- coding: utf-8 -*-
# Copyright (C) 2016-TODAY touch:n:track <https://tnt.pythonanywhere.com>
# Part of tnt: Flespi Receiver addon for Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http

class RouterController(http.Controller):
    @http.route([
        '/leaflet/router',
    ], type='json', auth='none')  # , methods=['POST'], csrf=False, website=True
    def leaflet_router(self, **post):
        data = []

        record_id = post.get('id')
        record = http.request.env['tnt.router'].browse(record_id)
        # customers = http.request.env['tnt.router'].search([('id', '=', record_id)]).customers
        customers = record.customers
        from_customer = record.from_customer
        d = {
            'id': from_customer.id,
            'name': from_customer.name,
            'pos_lat': from_customer.partner_latitude,
            'pos_lon': from_customer.partner_longitude,
            'from_customer': True,
            'data': [],
        }
        data.append(d)

        for customer in customers:
            d = {
                'id': customer.id,
                'name': customer.name,
                'pos_lat': customer.partner_latitude,
                'pos_lon': customer.partner_longitude,
                'data': [],
            }

            # domain = [('device_id', '=', device.id)]
            #
            # ts_from = post.get('ts_from', 0)
            # if ts_from:
            #     domain.append(('ts', '>=', ts_from))
            #
            # ts_to = post.get('ts_to', 0)
            # if ts_to:
            #     domain.append(('ts', '<=', ts_to))
            #
            # for log in http.request.env['tnt.flespi.device.log'].search(domain):
            #     d['data'].append({
            #         'ts': device.ts,
            #         'pos_lat': log.pos_lat,
            #         'pos_lon': log.pos_lon,
            #     })
            #
            # if ts_to and d['data']:
            #     d['pos_lat'] = d['data'][0]['pos_lat']
            #     d['pos_lon'] = d['data'][0]['pos_lon']

            data.append(d)

        return data