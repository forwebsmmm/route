# -*- coding: utf-8 -*-
# Copyright (C) 2016-TODAY touch:n:track <https://tnt.pythonanywhere.com>
# Part of tnt: Router addon for Odoo. See LICENSE file for full copyright and licensing details.
#sadasdasf

import openrouteservice

from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from odoo import models, fields, api
from odoo import http


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
        coordinates = []
        points = []

        record_id = self.id
        record = self
        profile = record.transport_type
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

        coords = [(coordinate['pos_lon'], coordinate['pos_lat']) for coordinate in coordinates]
        # coords = ((38.52385, 48.93983), (38.48984, 48.94444), (38.50923, 48.93922), (38.47977, 48.94691), (38.496496, 48.949443))
        # token = '5b3ce3597851110001cf62484562e6e6e3774f3aa7cfef13cdd0ec72'
        token = '5b3ce3597851110001cf6248b6aaf19581da4b7b83266ae376f097d6'

        clnt = openrouteservice.Client(key=token)
        addresses = []
        for feat in coords:
            lon, lat = feat
            name = clnt.pelias_reverse(point=(lon, lat))[
                'features'][0]['properties']['name']
            addresses.append(name)

        request = {'locations': coords,
                   'profile': profile,
                   'metrics': ['duration']}
        distance_matrix = clnt.distance_matrix(**request)

        tsp_size = len(addresses)
        num_routes = 1
        start = 0

        optimal_coords = []

        if tsp_size > 0:
            # Create the routing index manager.
            manager = pywrapcp.RoutingIndexManager(tsp_size, num_routes, start)
            # Create Routing Model.
            routing = pywrapcp.RoutingModel(manager)
            # Setting first solution heuristic.
            search_parameters = pywrapcp.DefaultRoutingSearchParameters()
            search_parameters.first_solution_strategy = (
                routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

            # Define cost of each arc.
            def distance_callback(from_index, to_index):
                """Returns the distance between the two nodes."""
                # Convert from routing variable Index to distance matrix NodeIndex.
                from_node = manager.IndexToNode(from_index)
                to_node = manager.IndexToNode(to_index)
                return int(distance_matrix['durations'][from_node][to_node])

            transit_callback_index = routing.RegisterTransitCallback(
                distance_callback)
            routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

            # Solve the problem.
            assignment = routing.SolveWithParameters(search_parameters)

            if assignment:
                # Index of the variable for the starting node.
                index = routing.Start(start)
                point_numbers = []
                for node in range(routing.nodes()):
                    optimal_coords.append(coords[manager.IndexToNode(index)])

                    point_numbers.append(manager.IndexToNode(index))

                    index = assignment.Value(routing.NextVar(index))

                optimal_coords.append(coords[manager.IndexToNode(index)])

                point_numbers.append(manager.IndexToNode(index))

        routes = clnt.directions(optimal_coords, profile=profile, optimize_waypoints=True)
        geometry = clnt.directions(optimal_coords)['routes'][0]['geometry']
        decoded = openrouteservice.convert.decode_polyline(geometry)

        if (decoded):
            route_coordinates = decoded['coordinates']

            rm = http.request.env['tnt.router.sequence'].search([('route', '=', record_id)]).unlink()

            for i, num in enumerate(point_numbers):
                new_record = http.request.env['tnt.router.sequence'].create({
                    'route': coordinates[num]['route_id'],
                    'sequence': i,
                    'customer': coordinates[num]['id'],
                    'latitude': coordinates[num]['pos_lat'],
                    'longitude': coordinates[num]['pos_lon']
                })

            for location in route_coordinates:
                d = {
                    'route': record_id,
                    'latitude': location[1],
                    'longitude': location[0]
                }
                points.append(d)

            rm = http.request.env['tnt.router.point'].search([('route', '=', record_id)]).unlink()
            for point in points:
                new_point = http.request.env['tnt.router.point'].create(point)
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
