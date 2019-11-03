# -*- coding: utf-8 -*-
{
    'name': "tnt: router",

    'summary': """
        Leaflet Router
    """,

    'description': """
        Add Leaflet Router
    """,

    'author': "touch:n:track",
    'website': "https://tnt.pythonanywhere.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Extra Tools',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'sale_management',
        'tnt_widget_leaflet',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/tnt_router_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}