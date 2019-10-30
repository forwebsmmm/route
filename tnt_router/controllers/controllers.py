# -*- coding: utf-8 -*-
from odoo import http

# class TntRouter(http.Controller):
#     @http.route('/tnt_router/tnt_router/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tnt_router/tnt_router/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tnt_router.listing', {
#             'root': '/tnt_router/tnt_router',
#             'objects': http.request.env['tnt_router.tnt_router'].search([]),
#         })

#     @http.route('/tnt_router/tnt_router/objects/<model("tnt_router.tnt_router"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tnt_router.object', {
#             'object': obj
#         })