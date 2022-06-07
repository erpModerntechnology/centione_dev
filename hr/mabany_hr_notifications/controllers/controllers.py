# -*- coding: utf-8 -*-
# from odoo import http


# class MabanyHrNotifications(http.Controller):
#     @http.route('/mabany_hr_notifications/mabany_hr_notifications', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mabany_hr_notifications/mabany_hr_notifications/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('mabany_hr_notifications.listing', {
#             'root': '/mabany_hr_notifications/mabany_hr_notifications',
#             'objects': http.request.env['mabany_hr_notifications.mabany_hr_notifications'].search([]),
#         })

#     @http.route('/mabany_hr_notifications/mabany_hr_notifications/objects/<model("mabany_hr_notifications.mabany_hr_notifications"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mabany_hr_notifications.object', {
#             'object': obj
#         })
