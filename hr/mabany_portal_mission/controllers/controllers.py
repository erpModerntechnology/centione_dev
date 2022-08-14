# -*- coding: utf-8 -*-
import math
from odoo import exceptions

from werkzeug import urls

from odoo import fields as odoo_fields, tools, _
from odoo.exceptions import ValidationError
from odoo.http import Controller, request, route, Response
from datetime import datetime, timedelta
from odoo.exceptions import UserError, AccessError, ValidationError


class MissionPortal(Controller):

    # all missions page
    @route(['/my/missions'], type='http', auth="user", website=True)
    def myMissions(self, **kw):
        def add_2hours_to_datetime(date):
            if date:
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

        # get mission types
        missions = {}
        types = ['normal', 'external', 'overnight']

        # get missions for these mission types
        if employee_id:
            missions = request.env['hr.mission'].sudo().search(
                [('employee_id', '=', employee_id.id),
                 ])
        vals['missions'] = missions

        return request.render("mabany_portal_mission.my_missions", vals)

    # prepare mission creation form
    @route(['/my/mission/create'], type='http', auth="user", website=True)
    def myMissionsCreate(self, vals={}, **kw):
        if 'error' not in vals:
            vals['error'] = {}

        return request.render("mabany_portal_mission.my_mission", vals)

    # specific mission page
    @route(['/my/mission/<int:mission_id>'], type='http', auth="user", website=True)
    def myMission(self, mission_id=0, **kw):
        def add_2hours_to_datetime(date):
            if date:
                # date = datetime.strptime(str(date).split(' ')[0], '%Y-%m-%d')
                return (date + timedelta(hours=2)).strftime("%m/%d/%Y %I:%M %p")
            else:
                return False

        vals = {}
        vals['error'] = {}
        vals['add_2hours_to_datetime'] = add_2hours_to_datetime

        if mission_id > 0:
            vals['mission'] = request.env['hr.mission'].sudo().browse(mission_id)
        return request.render("mabany_portal_mission.my_mission", vals)

    #
    # def send_email_to_approvers(self, employee_id, email_to):
    #
    #     body = '''
    #             Dear,<br>
    #             <pre>
    #     Kindly noted that Employee {employee} Requested a mission, Waiting for your approval.
    #             <br>
    #             Best Regards,
    #             </pre>'''.format(employee=employee_id.display_name, )
    #     mail_server = request.env['ir.mail_server'].sudo().search([], limit=1)
    #     mail_values = {
    #         'subject': "Mission Request Notification",
    #         'body_html': body,
    #         'email_to': email_to,
    #         'email_from': mail_server.smtp_user
    #     }
    #     approval_mail = request.env['mail.mail'].sudo().create(mail_values)
    #     approval_mail.sudo().send()
    #

    @route(['/my/mission/update'], type='http', auth="user", website=True)
    def myMissionUpdate(self, mission_id, **post):
        if mission_id != '':
            mission_id = int(mission_id)
            if mission_id > 0:
                mission_id = request.env['hr.mission'].sudo().browse(mission_id)
                if mission_id and 'delete_btn' in post and mission_id.state == 'draft':
                    mission_id.unlink()
                elif mission_id:
                    post['start_date'] = (datetime.strptime(post['start_date'], "%m/%d/%Y %I:%M %p") - timedelta(
                        hours=2)).strftime("%Y-%m-%d %H:%M:%S")
                    post['end_date'] = (
                                datetime.strptime(post['end_date'], "%m/%d/%Y %I:%M %p") - timedelta(hours=2)).strftime(
                        "%Y-%m-%d %H:%M:%S")

                    mission_id.write(post)
        else:
            post['employee_id'] = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.uid)]).id
            try:
                post['state'] = 'draft'
                post['start_date'] = (
                        datetime.strptime(post['start_date'], "%m/%d/%Y %I:%M %p") - timedelta(hours=2)).strftime(
                    "%Y-%m-%d %H:%M:%S")
                post['end_date'] = (
                        datetime.strptime(post['end_date'], "%m/%d/%Y %I:%M %p") - timedelta(hours=2)).strftime(
                    "%Y-%m-%d %H:%M:%S")

                mission_id = request.env['hr.mission'].sudo().create(post)

                # send mail to missions approve responsible persons
                # 1- for manager of the employee
                # self.send_email_to_approvers(mission_id.employee_id,mission_id.employee_id.parent_id.work_email)
                # #2- for second approval group
                # approvers= request.env.ref('portal_mission.mission_second_approvers').sudo().users
                # approvers = approvers.mapped('email')
                # for approver_user in approvers:
                #     self.sudo().send_email_to_approvers(mission_id.employee_id, approver_user)

                # mission_id._onchange_start_date()
            except Exception as exc:
                request._cr.rollback()
                post['error_message'] = "Error " + str(exc) + ' '
                return self.myMissionsCreate(post)
                # pass
                # return request.redirect('/my/missions')
        return request.redirect('/my/missions')

    @route(['/my/mission/delete'], type='http', auth="user", website=True)
    def myMissionDelete(self, **post):
        for key, value in post.items():
            if key.isdigit():
                mission_id = int(key)
                mission_id = request.env['hr.mission'].sudo().browse(mission_id)
                if mission_id:
                    mission_id.sudo().unlink()
        return request.redirect('/my/missions')
