# -*- coding: utf-8 -*-
# from odoo import http


# class MabanyExcusePeriod(http.Controller):
#     @http.route('/mabany_excuse_period/mabany_excuse_period', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mabany_excuse_period/mabany_excuse_period/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('mabany_excuse_period.listing', {
#             'root': '/mabany_excuse_period/mabany_excuse_period',
#             'objects': http.request.env['mabany_excuse_period.mabany_excuse_period'].search([]),
#         })

#     @http.route('/mabany_excuse_period/mabany_excuse_period/objects/<model("mabany_excuse_period.mabany_excuse_period"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mabany_excuse_period.object', {
#             'object': obj
#         })
