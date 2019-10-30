# -*- coding: utf-8 -*-
# Copyright (C) 2016-TODAY touch:n:track <https://tnt.pythonanywhere.com>
# Part of tnt: Flespi Monitoring addon for Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class TntFlespiDeviceLog(models.Model):
    _inherit = 'tnt.flespi.device.log'

    device_name = fields.Char(compute='_compute_device_name')

    @api.depends('device_id')
    def _compute_device_name(self):
        for record in self:
            record.device_name = record.device_id.display_name
