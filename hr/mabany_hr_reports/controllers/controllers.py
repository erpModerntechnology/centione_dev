# -*- coding: utf-8 -*-
# from odoo import http


# class MabanyReports(http.Controller):
#     @http.route('/mabany_reports/mabany_reports', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mabany_reports/mabany_reports/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('mabany_reports.listing', {
#             'root': '/mabany_reports/mabany_reports',
#             'objects': http.request.env['mabany_reports.mabany_reports'].search([]),
#         })

#     @http.route('/mabany_reports/mabany_reports/objects/<model("mabany_reports.mabany_reports"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mabany_reports.object', {
#             'object': obj
#         })
