# -*- coding: utf-8 -*-
import math
from odoo import exceptions

from werkzeug import urls

from odoo import fields as odoo_fields, tools, _
from odoo.exceptions import ValidationError
from odoo.http import Controller, request, route, Response
from datetime import datetime, timedelta
from odoo.exceptions import UserError, AccessError, ValidationError


class AttendancePortal(Controller):

    # all attendances page
    @route(['/my/attendances'], type='http', auth="user", website=True)
    def myAttendances(self, **kw):
        def convert_datetime_to_date(date):
            if date:
                return str(date).split(' ')[0]
            else:
                return False

        get_class_state_dict = {}
        get_description_state_dict = {}
        vals = {}
        vals['convert_datetime_to_date'] = convert_datetime_to_date
        vals['get_description_state_dict'] = get_description_state_dict
        vals['get_class_state_dict'] = get_class_state_dict

        # get employee has the current user as related user
        employee_id = request.env['hr.employee'].sudo().search([('user_id', '=', request.uid)])

        # get attendance types
        attendances = {}

        # get attendances for these attendance types
        if employee_id:
            attendances = request.env['hr.attendance'].sudo().search(
                [('employee_id', '=', employee_id.id)
                 ])
        vals['attendances'] = attendances

        return request.render("mabany_portal_attendance.my_attendances", vals)

    # prepare attendance creation form
    @route(['/my/attendance/create'], type='http', auth="user", website=True)
    def myAttendancesCreate(self, vals={}, **kw):
        if 'error' not in vals:
            vals['error'] = {}

        return request.render("mabany_portal_attendance.my_attendance", vals)

    # specific attendance page
    @route(['/my/attendance/<int:attendance_id>'], type='http', auth="user", website=True)
    def myAttendance(self, attendance_id=0, **kw):
        def convert_datetime_to_date(date):
            if date:
                date = datetime.strptime(str(date).split(' ')[0], '%Y-%m-%d')
                return date.strftime("%Y-%m-%d")
            else:
                return False

        vals = {}
        vals['error'] = {}
        vals['convert_datetime_to_date'] = convert_datetime_to_date

        if attendance_id > 0:
            vals['attendance'] = request.env['hr.attendance'].sudo().browse(attendance_id)
        return request.render("mabany_portal_attendance.my_attendance", vals)

    #
    # def send_email_to_approvers(self, employee_id, email_to):
    #
    #     body = '''
    #             Dear,<br>
    #             <pre>
    #     Kindly noted that Employee {employee} Requested a attendance, Waiting for your approval.
    #             <br>
    #             Best Regards,
    #             </pre>'''.format(employee=employee_id.display_name, )
    #     mail_server = request.env['ir.mail_server'].sudo().search([], limit=1)
    #     mail_values = {
    #         'subject': "Attendance Request Notification",
    #         'body_html': body,
    #         'email_to': email_to,
    #         'email_from': mail_server.smtp_user
    #     }
    #     approval_mail = request.env['mail.mail'].sudo().create(mail_values)
    #     approval_mail.sudo().send()
    #

    @route(['/my/attendance/update'], type='http', auth="user", website=True)
    def myAttendanceUpdate(self, attendance_id, **post):
        if attendance_id != '':
            attendance_id = int(attendance_id)
            if attendance_id > 0:
                attendance_id = request.env['hr.attendance'].sudo().browse(attendance_id)
                if attendance_id and post.get('to_delete') == "on":
                    attendance_id.unlink()
                elif attendance_id:
                    attendance_id.update(post)
        else:
            post['employee_id'] = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.uid)]).id
            try:
                post['state'] = 'draft'
                attendance_id = request.env['hr.attendance'].sudo().create(post)

            except Exception as exc:
                request._cr.rollback()
                post['error_message'] = "Error " + str(exc) + ' '
                return self.myAttendancesCreate(post)
                # pass
                # return request.redirect('/my/attendances')
        return request.redirect('/my/attendances')

    @route(['/my/attendance/delete'], type='http', auth="user", website=True)
    def myAttendanceDelete(self, **post):
        for key, value in post.items():
            if key.isdigit():
                attendance_id = int(key)
                attendance_id = request.env['hr.attendance'].sudo().browse(attendance_id)
                if attendance_id:
                    attendance_id.sudo().unlink()
        return request.redirect('/my/attendances')
