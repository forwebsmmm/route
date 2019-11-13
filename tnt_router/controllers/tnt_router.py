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

        return points