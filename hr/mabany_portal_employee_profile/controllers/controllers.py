# -*- coding: utf-8 -*-
import math
from odoo import exceptions

from werkzeug import urls

from odoo import fields as odoo_fields, tools, _
from odoo.exceptions import ValidationError
from odoo.http import Controller, request, route, Response
from datetime import datetime, timedelta
from odoo.exceptions import UserError, AccessError, ValidationError


class EmployeePortal(Controller):

    # employee list page
    @route(['/my/employees'], type='http', auth="user", website=True)
    def myEmployees(self, **kw):
        def convert_datetime_to_date(date):
            if date:
                return str(date).split(' ')[0]
            else:
                return False

        get_class_state_dict = {'cancel': 'label label-danger', 'closed': 'label label-danger',
                                'approved': 'label label-info',
                                'draft': 'label label-warning',
                                'sent': 'label label-success'}
        get_description_state_dict = {'draft': 'Draft', 'approved': 'Approved',
                                      'cancel': 'Cancelled', 'sent': 'Sent', 'closed': 'Closed', }
        vals = {}
        vals['convert_datetime_to_date'] = convert_datetime_to_date
        vals['get_description_state_dict'] = get_description_state_dict
        vals['get_class_state_dict'] = get_class_state_dict

        # get employee has the current user as related user
        employee_id = request.env['hr.employee'].sudo().search([('user_id', '=', request.uid)])

        # get employee types
        employees = {}

        # get employees for these employee types
        if employee_id:
            employees = request.env['hr.employee'].sudo().search(
                [('id', '=', employee_id.id)
                 ])
        vals['employees'] = employees

        return request.render("mabany_portal_employee_profile.my_employees", vals)

    # prepare employee creation form
    # @route(['/my/employee/create'], type='http', auth="user", website=True)
    # def myEmployeesCreate(self, vals={}, **kw):
    #     if 'error' not in vals:
    #         vals['error'] = {}
    #
    #     return request.render("mabany_portal_employee_profile.my_employee", vals)

    # specific employee page
    @route(['/my/employee/<int:employee_id>'], type='http', auth="user", website=True)
    def myEmployee(self, employee_id=0, **kw):
        def convert_datetime_to_date(date):
            if date:
                date = datetime.strptime(str(date).split(' ')[0], '%Y-%m-%d')
                return date.strftime("%Y-%m-%d")
            else:
                return False

        vals = {}
        vals['error'] = {}
        vals['convert_datetime_to_date'] = convert_datetime_to_date

        if employee_id > 0:
            vals['employee'] = request.env['hr.employee'].sudo().browse(employee_id)
        return request.render("mabany_portal_employee_profile.my_employee", vals)

    #
    # def send_email_to_approvers(self, employee_id, email_to):
    #
    #     body = '''
    #             Dear,<br>
    #             <pre>
    #     Kindly noted that Employee {employee} Requested a employee, Waiting for your approval.
    #             <br>
    #             Best Regards,
    #             </pre>'''.format(employee=employee_id.display_name, )
    #     mail_server = request.env['ir.mail_server'].sudo().search([], limit=1)
    #     mail_values = {
    #         'subject': "Employee Request Notification",
    #         'body_html': body,
    #         'email_to': email_to,
    #         'email_from': mail_server.smtp_user
    #     }
    #     approval_mail = request.env['mail.mail'].sudo().create(mail_values)
    #     approval_mail.sudo().send()
    #

    @route(['/my/employee/update'], type='http', auth="user", website=True)
    def myEmployeeUpdate(self, employee_id, **post):
        if employee_id != '':
            employee_id = int(employee_id)
            if employee_id > 0:
                employee_id = request.env['hr.employee'].sudo().browse(employee_id)
                if employee_id and post.get('to_delete') == "on":
                    employee_id.unlink()
                elif employee_id:
                    employee_id.update(post)
        else:
            post['employee_id'] = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.uid)]).id
            try:
                # employee_id = request.env['hr.employee'].sudo().create(post)
                pass

                # send mail to employees approve responsible persons
                # 1- for manager of the employee
                # self.send_email_to_approvers(employee_id.employee_id,employee_id.employee_id.parent_id.work_email)
                # #2- for second approval group
                # approvers= request.env.ref('portal_employee.employee_second_approvers').sudo().users
                # approvers = approvers.mapped('email')
                # for approver_user in approvers:
                #     self.sudo().send_email_to_approvers(employee_id.employee_id, approver_user)

                # employee_id._onchange_start_date()
            except Exception as exc:
                request._cr.rollback()
                post['error_message'] = "Error " + str(exc) + ' '
                return self.myEmployeesCreate(post)
        return request.redirect('/my/employees')

    @route(['/my/employee/delete'], type='http', auth="user", website=True)
    def myEmployeeDelete(self, **post):
        for key, value in post.items():
            if key.isdigit():
                employee_id = int(key)
                employee_id = request.env['hr.employee'].sudo().browse(employee_id)
                if employee_id:
                    employee_id.sudo().unlink()
        return request.redirect('/my/employees')
