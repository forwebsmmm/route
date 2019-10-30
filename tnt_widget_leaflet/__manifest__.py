# -*- coding: utf-8 -*-
# Copyright (C) 2016-TODAY touch:n:track <https://tnt.pythonanywhere.com>
# Part of tnt: Widget Leaflet addon for Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'tnt: Widget Leaflet',

    'summary': """
Leaflet Marker and Monitor
    """,

    'description': """
Add Leaflet Marker and Monitor widgets
    """,

    "author": "touch:n:track",
    "website": "https://tnt.pythonanywhere.com/",
    'category': 'Extra Tools',
    'version': '0.1',

    # "images": ['images/main_screenshot.png'],

    'depends': [
        'web',
    ],

    'data': [
        'views/web_leaflet_assets.xml'
    ],

    # 'demo': [
    #     'demo/demo.xml',
    # ],

    'qweb': [
        'static/src/xml/resource.xml'
    ],

    'bootstrap': True,

    'installable': True,
    'application': False,
    'auto_install': False,
}
