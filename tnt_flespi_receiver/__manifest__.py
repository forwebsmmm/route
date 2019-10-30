# -*- coding: utf-8 -*-
# Copyright (C) 2016-TODAY touch:n:track <https://tnt.pythonanywhere.com>
# Part of tnt: Flespi Receiver addon for Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'tnt: Flespi Receiver',

    'summary': """
Flespi HTTP Stream Receiver
    """,

    'description': """
Add /flespi controller to receive the telemetry data from the flespi platform via HTTP stream:

https://flespi.com/kb/how-to-get-data-in-your-platform-via-flespi-http-stream

Save data to Flespi Device and Flespi Device Log models
    """,

    "author": "touch:n:track",
    "website": "https://tnt.pythonanywhere.com/",
    'category': 'Extra Tools',
    'version': '0.1',

    'depends': [
        'base',
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/flespi_device_views.xml',
        'views/flespi_device_log_views.xml',
    ],

    'installable': True,
    'application': False,
    'auto_install': False,
}
