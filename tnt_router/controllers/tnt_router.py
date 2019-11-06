# -*- coding: utf-8 -*-
# Copyright (C) 2016-TODAY touch:n:track <https://tnt.pythonanywhere.com>
# Part of tnt: Router addon for Odoo. See LICENSE file for full copyright and licensing details.
import requests
import json

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

    @http.route([
        '/leaflet/generate',
    ], type='json', auth='none')  # , methods=['POST'], csrf=False, website=True
    def leaflet_generate(self, **post):
        coordinates = []
        data = []
        points = []

        record_id = post.get('id')
        record = http.request.env['tnt.router'].browse(record_id)
        customers = record.customers
        from_customer = record.from_customer
        d = {
            'id': from_customer.id,
            'pos_lat': from_customer.partner_latitude,
            'pos_lon': from_customer.partner_longitude,
            'route_id': record_id,
        }
        coordinates.append(d)

        for customer in customers:
            d = {
                'id': customer.id,
                'pos_lat': customer.partner_latitude,
                'pos_lon': customer.partner_longitude,
                'route_id': record_id,
            }

            coordinates.append(d)

        url = 'http://router.project-osrm.org/trip/v1/driving/'
        for coordinate in coordinates:
            separator = ';' if coordinate != coordinates[-1] else ''
            url += str(coordinate['pos_lat']) + ',' + str(coordinate['pos_lon']) + separator

        route_params = {'source': 'first'}
        r = requests.get(url, params=route_params)

        if (r.status_code == 200):
            parsed_json = (json.loads(r.content))
            waypoints = parsed_json['waypoints']

            for i, point in enumerate(waypoints):
                coordinates[i]['waypoint_index'] = point['waypoint_index']
                coordinates[i]['pos_lat'] = point['location'][0]
                coordinates[i]['pos_lon'] = point['location'][1]

            rm = http.request.env['tnt.router.sequence'].search([('route', '=', record_id)]).unlink()
            for coordinate in coordinates:
                new_record = http.request.env['tnt.router.sequence'].create({
                    'route': coordinate['route_id'],
                    'sequence': coordinate['waypoint_index'],
                    'customer': coordinate['id'],
                    'latitude': coordinate['pos_lat'],
                    'longitude': coordinate['pos_lon']
                })

            sorted_records = http.request.env['tnt.router.sequence'].search([('route', '=', record_id)])
            url = 'http://router.project-osrm.org/route/v1/driving/'
            for coordinate in sorted_records:
                separator = ';' if coordinate != sorted_records[-1] else ''
                url += str(coordinate['latitude']) + ',' + str(coordinate['longitude']) + separator

            point_params = {'steps': 'true'}
            r = requests.get(url, params=point_params)

            if (r.status_code == 200):
                parsed_json = (json.loads(r.content))
                legs = parsed_json['routes'][0]['legs']
                for i, leg in enumerate(legs):
                    steps = leg['steps']
                    d = {
                        'sequence': i,
                        'route': record_id,
                    }
                    for step in steps:
                        location = step['maneuver']['location']
                        d['latitude'] = location[0]
                        d['longitude'] = location[1]
                        points.append(d)

                rm = http.request.env['tnt.router.point'].search([('route', '=', record_id)]).unlink()
                for point in points:
                    new_point = http.request.env['tnt.router.point'].create(point)

        return points