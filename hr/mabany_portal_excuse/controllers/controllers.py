# -*- coding: utf-8 -*-
import math
from odoo import exceptions

from werkzeug import urls

from odoo import fields as odoo_fields, tools, _
from odoo.exceptions import ValidationError
from odoo.http import Controller, request, route, Response
from datetime import datetime, timedelta
from odoo.exceptions import UserError, AccessError, ValidationError


class ExcusePortal(Controller):

    # all excuses page
    @route(['/my/excuses'], type='http', auth="user", website=True)
    def myExcuses(self, **kw):
        def add_2hours_to_datetime(date):
            if date:
                # return str(date).split(' ')[0]
                return (date + timedelta(hours=2)).strftime('%m/%d/%Y %I:%M %p')

            else:
                return False

        get_class_state_dict = {'refuse': 'label label-danger', 'approve': 'label label-info',
                                'draft': 'label label-warning',
                                'validate': 'label label-success'}
        get_description_state_dict = {'draft': 'Draft', 'approve': 'Approved',
                                      'refuse': 'Refused', 'validate': 'Validated', }
        vals = {}
        vals['add_2hours_to_datetime'] = add_2hours_to_datetime
        vals['get_description_state_dict'] = get_description_state_dict
        vals['get_class_state_dict'] = get_class_state_dict

        # get employee has the current user as related user
        employee_id = request.env['hr.employee'].sudo().search([('user_id', '=', request.uid)])

        # get excuse types
        excuses = {}

        # get excuses for these excuse types
        if employee_id:
            excuses = request.env['hr.excuse'].sudo().search(
                [('employee_id', '=', employee_id.id)
                 ])
        vals['excuses'] = excuses

        return request.render("mabany_portal_excuse.my_excuses", vals)

    # prepare excuse creation form
    @route(['/my/excuse/create'], type='http', auth="user", website=True)
    def myExcusesCreate(self, vals={}, **kw):
        if 'error' not in vals:
            vals['error'] = {}

        return request.render("mabany_portal_excuse.my_excuse", vals)

    # specific excuse page
    @route(['/my/excuse/<int:excuse_id>'], type='http', auth="user", website=True)
    def myExcuse(self, excuse_id=0, **kw):
        def add_2hours_to_datetime(date):
            if date:
                # date = datetime.strptime(str(date).split(' ')[0], '%Y-%m-%d')
                # return date.strftime("%Y-%m-%d")
                return (date + timedelta(hours=2)).strftime('%m/%d/%Y %I:%M %p')

            else:
                return False

        vals = {}
        vals['error'] = {}
        vals['add_2hours_to_datetime'] = add_2hours_to_datetime
        vals['excuse_types_'] = ['normal', 'external', 'overnight']

        if excuse_id > 0:
            vals['excuse'] = request.env['hr.excuse'].sudo().browse(excuse_id)
        return request.render("mabany_portal_excuse.my_excuse", vals)

    #
    # def send_email_to_approvers(self, employee_id, email_to):
    #
    #     body = '''
    #             Dear,<br>
    #             <pre>
    #     Kindly noted that Employee {employee} Requested a excuse, Waiting for your approval.
    #             <br>
    #             Best Regards,
    #             </pre>'''.format(employee=employee_id.display_name, )
    #     mail_server = request.env['ir.mail_server'].sudo().search([], limit=1)
    #     mail_values = {
    #         'subject': "Excuse Request Notification",
    #         'body_html': body,
    #         'email_to': email_to,
    #         'email_from': mail_server.smtp_user
    #     }
    #     approval_mail = request.env['mail.mail'].sudo().create(mail_values)
    #     approval_mail.sudo().send()
    #

    @route(['/my/excuse/update'], type='http', auth="user", website=True)
    def myExcuseUpdate(self, excuse_id, **post):
        if excuse_id != '':
            excuse_id = int(excuse_id)
            if excuse_id > 0:
                excuse_id = request.env['hr.excuse'].sudo().browse(excuse_id)
                if excuse_id and post.get('to_delete') == "on":
                    excuse_id.unlink()
                elif excuse_id:
                    post['start_date'] = (
                            datetime.strptime(post['start_date'],
                                              "%m/%d/%Y %I:%M %p") - timedelta(
                        hours=2)).strftime(
                        "%Y-%m-%d %H:%M:%S")
                    post['end_date'] = (
                            datetime.strptime(post['end_date'],
                                              "%m/%d/%Y %I:%M %p") - timedelta(
                        hours=2)).strftime(
                        "%Y-%m-%d %H:%M:%S")

                    excuse_id.write(post)
        else:
            post['employee_id'] = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.uid)]).id
            try:
                post['state'] = 'draft'
                post['start_date'] = (
                        datetime.strptime(post['start_date'],
                                          "%m/%d/%Y %I:%M %p") - timedelta(
                    hours=2)).strftime(
                    "%Y-%m-%d %H:%M:%S")
                post['end_date'] = (
                        datetime.strptime(post['end_date'],
                                          "%m/%d/%Y %I:%M %p") - timedelta(
                    hours=2)).strftime(
                    "%Y-%m-%d %H:%M:%S")

                excuse_id = request.env['hr.excuse'].sudo().create(post)

                # send mail to excuses approve responsible persons
                # 1- for manager of the employee
                # self.send_email_to_approvers(excuse_id.employee_id,excuse_id.employee_id.parent_id.work_email)
                # #2- for second approval group
                # approvers= request.env.ref('portal_excuse.excuse_second_approvers').sudo().users
                # approvers = approvers.mapped('email')
                # for approver_user in approvers:
                #     self.sudo().send_email_to_approvers(excuse_id.employee_id, approver_user)

                # excuse_id._onchange_start_date()
            except Exception as exc:
                request._cr.rollback()
                post['error_message'] = "Error " + str(exc) + ' '
                return self.myExcusesCreate(post)
                # pass
                # return request.redirect('/my/excuses')
        return request.redirect('/my/excuses')

    @route(['/my/excuse/delete'], type='http', auth="user", website=True)
    def myExcuseDelete(self, **post):
        for key, value in post.items():
            if key.isdigit():
                excuse_id = int(key)
                excuse_id = request.env['hr.excuse'].sudo().browse(excuse_id)
                if excuse_id:
                    excuse_id.sudo().unlink()
        return request.redirect('/my/excuses')
