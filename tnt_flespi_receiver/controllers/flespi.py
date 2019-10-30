# -*- coding: utf-8 -*-
# Copyright (C) 2016-TODAY touch:n:track <https://tnt.pythonanywhere.com>
# Part of tnt: Flespi Receiver addon for Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http

import json
import logging
import werkzeug

_logger = logging.getLogger(__name__)


class ExtJsonRequest(http.WebRequest):
    def __init__(self, *args):
        super(http.JsonRequest, self).__init__(*args)

        self.jsonp_handler = None
        self.params = {}

        args = self.httprequest.args
        jsonp = args.get('jsonp')
        self.jsonp = jsonp
        request = None
        request_id = args.get('id')

        if jsonp and self.httprequest.method == 'POST':
            # jsonp 2 steps step1 POST: save call
            def handler():
                self.session['jsonp_request_%s' % (request_id,)] = self.httprequest.form['r']
                self.session.modified = True
                headers = [('Content-Type', 'text/plain; charset=utf-8')]
                r = werkzeug.wrappers.Response(request_id, headers=headers)
                return r

            self.jsonp_handler = handler
            return
        elif jsonp and args.get('r'):
            # jsonp method GET
            request = args.get('r')
        elif jsonp and request_id:
            # jsonp 2 steps step2 GET: run and return result
            request = self.session.pop('jsonp_request_%s' % (request_id,), '{}')
        else:
            # regular jsonrpc2
            request = self.httprequest.get_data().decode(self.httprequest.charset)

        # Read POST content or POST Form Data named "request"
        try:
            self.jsonrequest = json.loads(request)
        except ValueError:
            msg = 'Invalid JSON data: %r' % (request,)
            _logger.info('%s: %s', self.httprequest.path, msg)
            raise werkzeug.exceptions.BadRequest(msg)

        if isinstance(self.jsonrequest, dict):
            self.params = dict(self.jsonrequest.get("params", {}))
        else:
            self.jsonrequest = {
                'id': None,
            }
            self.params = {
                'request': request
            }

        self.context = self.params.pop('context', dict(self.session.context))


http.JsonRequest.__init__ = ExtJsonRequest.__init__


class FlespiController(http.Controller):
    @http.route([
        '/flespi',
    ], type='json', auth='none', methods=['POST'], csrf=False)
    def flespi(self, **post):
        data = post.get('request', '')
        if data:
            for item in json.loads(data):
                ident = item.get('ident', '')
                if ident:
                    fields = {
                        'channel_id': item.get('channel.id', 0),
                        'peer': item.get('peer', ''),
                        'pos_alt': item.get('position.altitude', 0),
                        'pos_dir': item.get('position.direction', 0),
                        'pos_lat': item.get('position.latitude', 0),
                        'pos_lon': item.get('position.longitude', 0),
                        'pos_sat': item.get('position.satellites', 0),
                        'pos_spd': item.get('position.speed', 0),
                        'protocol_id': item.get('protocol.id', 0),
                        'server_ts': item.get('server.timestamp', 0),
                        'ts': item.get('timestamp', 0),

                        'battery_voltage': item.get('battery.voltage', 0),
                        'ext_power_voltage': item.get('external.powersource.voltage', 0),
                        'gsm_signal_level': item.get('gsm.signal.level', 0),
                        'din': item.get('din', 0),

                        'c_battery_charge': item.get('custom.battery_charge', 0),
                        'c_param5': item.get('custom.param5', 0),
                        'c_param100': item.get('custom.param100', 0),
                        'c_param101': item.get('custom.param101', 0),
                        'c_param112': item.get('custom.param112', 0),
                        'c_param113': item.get('custom.param113', 0),
                    }

                    flespi_device = http.request.env['tnt.flespi.device'].sudo().search([
                        ('ident', '=', ident),
                    ])

                    if flespi_device:
                        flespi_device = flespi_device[0]
                        flespi_device.write(fields)
                    else:
                        fields['ident'] = ident
                        fields['name'] = '{} (autocreated)'.format(ident)
                        flespi_device = flespi_device.create(fields)

                    if flespi_device.logs:
                        flespi_device_log = http.request.env['tnt.flespi.device.log'].sudo()
                        fields['device_id'] = flespi_device[0].id
                        flespi_device_log.create(fields)

        # raise werkzeug.exceptions.BadRequest("Flespi Bad Request")
        # return http.Response("Flespi OK", status=200)
        # return http.Response("Flespi Bad Request", status=400)

    @http.route([
        '/flespi/monitor',
    ], type='json', auth='none')  # , methods=['POST'], csrf=False, website=True
    def flespi_monitor(self, **post):
        data = []

        for device in http.request.env['tnt.flespi.device'].search([  # .sudo()
            ('id', 'in', post.get('ids', [])),
        ]):
            d = {
                'id': device.id,
                'name': device.name,
                'pos_lat': device.pos_lat,
                'pos_lon': device.pos_lon,
                'data': [],
            }

            domain = [('device_id', '=', device.id)]

            ts_from = post.get('ts_from', 0)
            if ts_from:
                domain.append(('ts', '>=', ts_from))

            ts_to = post.get('ts_to', 0)
            if ts_to:
                domain.append(('ts', '<=', ts_to))

            for log in http.request.env['tnt.flespi.device.log'].search(domain):
                d['data'].append({
                    'ts': device.ts,
                    'pos_lat': log.pos_lat,
                    'pos_lon': log.pos_lon,
                })

            if ts_to and d['data']:
                d['pos_lat'] = d['data'][0]['pos_lat']
                d['pos_lon'] = d['data'][0]['pos_lon']

            data.append(d)

        return data
