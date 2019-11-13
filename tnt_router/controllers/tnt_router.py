# -*- coding: utf-8 -*-
# Copyright (C) 2016-TODAY touch:n:track <https://tnt.pythonanywhere.com>
# Part of tnt: Router addon for Odoo. See LICENSE file for full copyright and licensing details.
import requests
import json
import openrouteservice

# from openrouteservice import client, distance_matrix, directions, convert
from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from scipy import spatial

from odoo import http

class RouterController(http.Controller):
    @http.route([
        '/leaflet/router',
    ], type='json', auth='none')  # , methods=['POST'], csrf=False, website=True
    def leaflet_router(self, **post):
        data = {
            'marker': [],
            'point': []
        }
        record_id = post.get('id')
        record = http.request.env['tnt.router'].browse(record_id)
        # customers = http.request.env['tnt.router'].search([('id', '=', record_id)]).customers
        customers = record.customers
        from_customer = record.from_customer
        points = record.points_ids
        d = {
            'id': from_customer.id,
            'name': from_customer.name,
            'pos_lat': from_customer.partner_latitude,
            'pos_lon': from_customer.partner_longitude,
            'from_customer': True,
            'data': [],
        }
        data['marker'].append(d)

        for customer in customers:
            d = {
                'id': customer.id,
                'name': customer.name,
                'pos_lat': customer.partner_latitude,
                'pos_lon': customer.partner_longitude,
                'data': [],
            }

            data['marker'].append(d)

        for point in points:
            d = {
                'pos_lat': point['latitude'],
                'pos_lon': point['longitude']
            }

            data['point'].append(d)


        return data