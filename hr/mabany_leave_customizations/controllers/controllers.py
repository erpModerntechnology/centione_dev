# -*- coding: utf-8 -*-
# from odoo import http


# class MabanyLeaveCustomizations(http.Controller):
#     @http.route('/mabany_leave_customizations/mabany_leave_customizations', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mabany_leave_customizations/mabany_leave_customizations/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('mabany_leave_customizations.listing', {
#             'root': '/mabany_leave_customizations/mabany_leave_customizations',
#             'objects': http.request.env['mabany_leave_customizations.mabany_leave_customizations'].search([]),
#         })

#     @http.route('/mabany_leave_customizations/mabany_leave_customizations/objects/<model("mabany_leave_customizations.mabany_leave_customizations"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mabany_leave_customizations.object', {
#             'object': obj
#         })
