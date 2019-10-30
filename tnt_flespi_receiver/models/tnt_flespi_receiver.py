# -*- coding: utf-8 -*-
# Copyright (C) 2016-TODAY touch:n:track <https://tnt.pythonanywhere.com>
# Part of tnt: Flespi Receiver addon for Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

from datetime import datetime


class TntFlespiDevice(models.Model):
    _name = 'tnt.flespi.device'
    _description = 'Flespi Devices'
    _order = 'name, create_date desc'
    _sql_constraints = [
        ('ident_unique', 'unique (ident)', "The Device Identifier must be unique"),
    ]

    ident = fields.Char(string='Device Identifier', required=True, index=True)
    name = fields.Char(string='Device Name', default='Device (autocreated)')

    log_ids = fields.One2many('tnt.flespi.device.log', 'device_id', 'Flespi Device Logs')
    logs = fields.Boolean(default=False)

    display_datetime = fields.Datetime(string='Date', compute='_compute_display_datetime')

    channel_id = fields.Integer(string='channel.id')
    peer = fields.Char(string='peer')
    pos_alt = fields.Integer(string='position.altitude')
    pos_dir = fields.Integer(string='position.direction')
    pos_lat = fields.Float(string='position.latitude', digits=(16, 6))
    pos_lon = fields.Float(string='position.longitude', digits=(16, 6))
    pos_sat = fields.Integer(string='position.satellites')
    pos_spd = fields.Integer(string='position.speed')
    protocol_id = fields.Integer(string='protocol.id')
    server_ts = fields.Float(string='server.timestamp', digits=(16, 6))
    ts = fields.Integer(string='timestamp')

    battery_voltage = fields.Float(string='battery.voltage', digits=(16, 3))
    ext_power_voltage = fields.Float(string='external.powersource.voltage', digits=(16, 3))
    gsm_signal_level = fields.Integer(string='gsm.signal.level')
    din = fields.Integer(string='din')
    c_battery_charge = fields.Integer(string='custom.battery_charge')
    c_param5 = fields.Integer(string='custom.param5')
    c_param100 = fields.Integer(string='custom.param100')
    c_param101 = fields.Integer(string='custom.param101')
    c_param112 = fields.Integer(string='custom.param112')
    c_param113 = fields.Integer(string='custom.param113')

    @api.depends('ts')
    def _compute_display_datetime(self):
        for record in self:
            record.display_datetime = datetime.fromtimestamp(record.ts)


class TntFlespiDeviceLog(models.Model):
    _name = 'tnt.flespi.device.log'
    _description = 'Flespi Device Logs'
    _order = 'ts desc'
    _sql_constraints = [
        ('device_id, ts', 'unique (device_id, ts)', "(device_id, ts) must be unique"),
    ]

    device_id = fields.Many2one('tnt.flespi.device', string='Flespi Device', ondelete='cascade')
    display_name = fields.Char(compute='_compute_display_name')
    display_datetime = fields.Datetime(string='Date', compute='_compute_display_datetime')

    channel_id = fields.Integer(string='channel.id')
    peer = fields.Char(string='peer')
    pos_alt = fields.Integer(string='position.altitude')
    pos_dir = fields.Integer(string='position.direction')
    pos_lat = fields.Float(string='position.latitude', digits=(16, 6))
    pos_lon = fields.Float(string='position.longitude', digits=(16, 6))
    pos_sat = fields.Integer(string='position.satellites')
    pos_spd = fields.Integer(string='position.speed')
    protocol_id = fields.Integer(string='protocol.id')
    server_ts = fields.Float(string='server.timestamp', digits=(16, 6))
    ts = fields.Integer(string='timestamp', index=True)

    battery_voltage = fields.Float(string='battery.voltage', digits=(16, 3))
    ext_power_voltage = fields.Float(string='external.powersource.voltage', digits=(16, 3))
    gsm_signal_level = fields.Integer(string='gsm.signal.level')
    din = fields.Integer(string='din')
    c_battery_charge = fields.Integer(string='custom.battery_charge')
    c_param5 = fields.Integer(string='custom.param5')
    c_param100 = fields.Integer(string='custom.param100')
    c_param101 = fields.Integer(string='custom.param101')
    c_param112 = fields.Integer(string='custom.param112')
    c_param113 = fields.Integer(string='custom.param113')

    @api.depends('display_datetime', 'device_id')
    def _compute_display_name(self):
        for record in self:
            record.display_name = '{} {}'.format(record.display_datetime, record.device_id.display_name)

    @api.depends('ts')
    def _compute_display_datetime(self):
        for record in self:
            record.display_datetime = datetime.fromtimestamp(record.ts)
