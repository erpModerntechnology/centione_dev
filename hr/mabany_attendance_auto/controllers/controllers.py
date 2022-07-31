# -*- coding: utf-8 -*-
# from odoo import http


# class MabanyAttendanceAuto(http.Controller):
#     @http.route('/mabany_attendance_auto/mabany_attendance_auto', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mabany_attendance_auto/mabany_attendance_auto/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('mabany_attendance_auto.listing', {
#             'root': '/mabany_attendance_auto/mabany_attendance_auto',
#             'objects': http.request.env['mabany_attendance_auto.mabany_attendance_auto'].search([]),
#         })

#     @http.route('/mabany_attendance_auto/mabany_attendance_auto/objects/<model("mabany_attendance_auto.mabany_attendance_auto"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mabany_attendance_auto.object', {
#             'object': obj
#         })
