# -*- coding: utf-8 -*-
# Copyright (C) 2016-TODAY touch:n:track <https://tnt.pythonanywhere.com>
# Part of tnt: Flespi Monitoring addon for Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class TntFlespiMonitoring(models.Model):
    _name = 'tnt.flespi.monitoring'
    _description = 'Flespi Monitoring'
    _order = 'name, create_date desc'

    name = fields.Char(string='Monitoring Name', default='Monitoring')
    device_ids = fields.Many2many('tnt.flespi.device', string='Flespi Devices', required=True)
    date_from = fields.Datetime(string='Date From')
    date_to = fields.Datetime(string='Date To')

    ts_from = fields.Integer(string='Timestamp From', compute='_compute_ts_from')
    ts_to = fields.Integer(string='Timestamp To', compute='_compute_ts_to')

    @api.depends('date_from')
    def _compute_ts_from(self):
        for record in self:
            record.ts_from = int(
                fields.Datetime.from_string(record.date_from).timestamp()) if record.date_from else None

    @api.depends('date_to')
    def _compute_ts_to(self):
        for record in self:
            record.ts_to = int(fields.Datetime.from_string(record.date_to).timestamp()) if record.date_to else None
