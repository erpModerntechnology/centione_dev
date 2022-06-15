# -*- coding: utf-8 -*-
import math
from odoo import exceptions

from werkzeug import urls

from odoo import fields as odoo_fields, tools, _
from odoo.exceptions import ValidationError
from odoo.http import Controller, request, route, Response
from datetime import datetime, timedelta
from odoo.exceptions import UserError, AccessError, ValidationError


class TerminationPortal(Controller):

    # all terminations page
    @route(['/my/terminations'], type='http', auth="user", website=True)
    def myTerminations(self, **kw):
        def convert_datetime_to_date(date):
            if date:
                return str(date).split(' ')[0]
            else:
                return False

        get_class_state_dict = {
                                'cancel': 'label label-danger',
                                'approved': 'label label-info',
                                'draft': 'label label-warning',
                                }
        get_description_state_dict = {'draft': 'Draft', 'approved': 'Approved',
                                      'cancel': 'Cancelled'  }
        vals = {}
        vals['convert_datetime_to_date'] = convert_datetime_to_date
        vals['get_description_state_dict'] = get_description_state_dict
        vals['get_class_state_dict'] = get_class_state_dict

        # get employee has the current user as related user
        employee_id = request.env['hr.employee'].sudo().search([('user_id', '=', request.uid)])

        # get termination types
        terminations = {}

        # get terminations for these termination types
        if employee_id:
            terminations = request.env['hr.termination'].sudo().search(
                [('employee_id', '=', employee_id.id)
                 ])
        vals['terminations'] = terminations

        return request.render("mabany_portal_termination.my_terminations", vals)

    # prepare termination creation form
    @route(['/my/termination/create'], type='http', auth="user", website=True)
    def myTerminationsCreate(self, vals={}, **kw):
        if 'error' not in vals:
            vals['error'] = {}

        return request.render("mabany_portal_termination.my_termination", vals)

    # specific termination page
    @route(['/my/termination/<int:termination_id>'], type='http', auth="user", website=True)
    def myTermination(self, termination_id=0, **kw):
        def convert_datetime_to_date(date):
            if date:
                date = datetime.strptime(str(date).split(' ')[0], '%Y-%m-%d')
                return date.strftime("%Y-%m-%d")
            else:
                return False

        vals = {}
        vals['error'] = {}
        vals['convert_datetime_to_date'] = convert_datetime_to_date

        if termination_id > 0:
            vals['termination'] = request.env['hr.termination'].sudo().browse(termination_id)
        return request.render("mabany_portal_termination.my_termination", vals)

    #
    # def send_email_to_approvers(self, employee_id, email_to):
    #
    #     body = '''
    #             Dear,<br>
    #             <pre>
    #     Kindly noted that Employee {employee} Requested a termination, Waiting for your approval.
    #             <br>
    #             Best Regards,
    #             </pre>'''.format(employee=employee_id.display_name, )
    #     mail_server = request.env['ir.mail_server'].sudo().search([], limit=1)
    #     mail_values = {
    #         'subject': "Termination Request Notification",
    #         'body_html': body,
    #         'email_to': email_to,
    #         'email_from': mail_server.smtp_user
    #     }
    #     approval_mail = request.env['mail.mail'].sudo().create(mail_values)
    #     approval_mail.sudo().send()
    #

    @route(['/my/termination/update'], type='http', auth="user", website=True)
    def myTerminationUpdate(self, termination_id, **post):
        if termination_id != '':
            termination_id = int(termination_id)
            if termination_id > 0:
                termination_id = request.env['hr.termination'].sudo().browse(termination_id)
                if termination_id and post.get('to_delete') == "on":
                    termination_id.unlink()
                elif termination_id:
                    termination_id.update(post)
        else:
            post['employee_id'] = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.uid)]).id
            try:
                post['state'] = 'draft'
                termination_id = request.env['hr.termination'].sudo().create(post)

                # send mail to terminations approve responsible persons
                # 1- for manager of the employee
                # self.send_email_to_approvers(termination_id.employee_id,termination_id.employee_id.parent_id.work_email)
                # #2- for second approval group
                # approvers= request.env.ref('portal_termination.termination_second_approvers').sudo().users
                # approvers = approvers.mapped('email')
                # for approver_user in approvers:
                #     self.sudo().send_email_to_approvers(termination_id.employee_id, approver_user)

                # termination_id._onchange_start_date()
            except Exception as exc:
                request._cr.rollback()
                post['error_message'] = "Error " + str(exc) + ' '
                return self.myTerminationsCreate(post)
                # pass
                # return request.redirect('/my/terminations')
        return request.redirect('/my/terminations')

    @route(['/my/termination/delete'], type='http', auth="user", website=True)
    def myTerminationDelete(self, **post):
        for key, value in post.items():
            if key.isdigit():
                termination_id = int(key)
                termination_id = request.env['hr.termination'].sudo().browse(termination_id)
                if termination_id:
                    termination_id.sudo().unlink()
        return request.redirect('/my/terminations')
