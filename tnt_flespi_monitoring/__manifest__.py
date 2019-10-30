# -*- coding: utf-8 -*-
# Copyright (C) 2016-TODAY touch:n:track <https://tnt.pythonanywhere.com>
# Part of tnt: Flespi Monitoring addon for Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'tnt: Flespi Monitoring',

    'summary': """
Device Monitoring for Flespi HTTP Stream Receiver
    """,

    'description': """
Add Leaflet Marker Widget to Flespi Device form view and Flespi Device Log form view

Add Flespi Monitoring model and Leaflet Monitor Widget to Flespi Monitoring form view
    """,

    "author": "touch:n:track",
    "website": "https://tnt.pythonanywhere.com/",
    'category': 'Extra Tools',
    'version': '0.1',

    'depends': [
        'tnt_flespi_receiver',
        'tnt_widget_leaflet',
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/flespi_monitoring_views.xml',
        'views/flespi_device_log_views.xml',
    ],

    'installable': True,
    'application': False,
    'auto_install': False,
}
