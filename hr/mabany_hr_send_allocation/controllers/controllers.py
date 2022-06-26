# -*- coding: utf-8 -*-
# from odoo import http


# class MabanyHrSendAllocation(http.Controller):
#     @http.route('/mabany_hr_send_allocation/mabany_hr_send_allocation', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mabany_hr_send_allocation/mabany_hr_send_allocation/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('mabany_hr_send_allocation.listing', {
#             'root': '/mabany_hr_send_allocation/mabany_hr_send_allocation',
#             'objects': http.request.env['mabany_hr_send_allocation.mabany_hr_send_allocation'].search([]),
#         })

#     @http.route('/mabany_hr_send_allocation/mabany_hr_send_allocation/objects/<model("mabany_hr_send_allocation.mabany_hr_send_allocation"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mabany_hr_send_allocation.object', {
#             'object': obj
#         })
