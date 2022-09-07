# -*- coding: utf-8 -*-
# from odoo import http


# class mabanyExcuseTimes(http.Controller):
#     @http.route('/mabany_excuse_times/mabany_excuse_times/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mabany_excuse_times/mabany_excuse_times/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mabany_excuse_times.listing', {
#             'root': '/mabany_excuse_times/mabany_excuse_times',
#             'objects': http.request.env['mabany_excuse_times.mabany_excuse_times'].search([]),
#         })

#     @http.route('/mabany_excuse_times/mabany_excuse_times/objects/<model("mabany_excuse_times.mabany_excuse_times"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mabany_excuse_times.object', {
#             'object': obj
#         })
