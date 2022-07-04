# -*- coding: utf-8 -*-
from datetime import timedelta, date

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

from odoo.http import request
import base64

class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    holiday_type = fields.Selection(
        [('marriage', 'جواز'), ('casual', 'عارضة'), ('sick', 'مرضى'), ('unpaid', 'غير مدفوع'), ('annual', 'سنوي')])
    exception_constraint = fields.Boolean('Exception Constraint')


class HrLeave(models.Model):
    _inherit = 'hr.leave'



    exception_constraint = fields.Boolean('Exception Constraint')

    @api.depends('date_from', 'date_to', 'employee_id','request_date_from','request_date_to',)
    def _compute_number_of_days(self):
        result = super(HrLeave, self)._compute_number_of_days()


        #if sick leave type,compute the number of days as diff bet dates +1
        for holiday in self:
            if holiday.holiday_status_id.holiday_type=='sick' and holiday.request_date_from and holiday.request_date_to:
                holiday.number_of_days= (holiday.request_date_to-holiday.request_date_from).days+1

        return result

    @api.constrains('request_date_from','request_date_to')
    def constraint_holiday_annual(self):
        leave_annual = self.env['hr.leave'].search(
            [('employee_id', '=', self.employee_id.id), ('holiday_status_id.holiday_type', '=', 'annual')])
        for leave in leave_annual:
            if leave.exception_constraint == False:
                if leave.request_date_from >= date.today() <= leave.request_date_to:
                    raise ValidationError(_("annual Holiday must be day before"))


    @api.constrains('number_of_days')
    def constraint_number_of_days_casual(self):
        total_dur_casual = []
        total_dur_marriage = []
        leave_casual = self.env['hr.leave'].search(
            [('employee_id', '=', self.employee_id.id), ('holiday_status_id.holiday_type', '=', 'casual')])
        leave_marriage = self.env['hr.leave'].search(
            [('employee_id', '=', self.employee_id.id), ('holiday_status_id.holiday_type', '=', 'marriage')])
        for lec in leave_casual:
            if lec.exception_constraint == False:
                total_dur_casual.append(lec.number_of_days)
                if sum(total_dur_casual) > 2:
                    raise ValidationError(_("Casual Holiday must not exceeds 2 days per month"))
        for lem in leave_marriage:
            total_dur_marriage.append(lem.number_of_days)
            if sum(total_dur_marriage) > 5:
                raise ValidationError(_("Marriage Holiday must not exceeds a week maximum"))

    def send_notification(self, partner_id, employee_name, leave_page_url):
        notification_ids = [(0, 0, {
            'res_partner_id': partner_id,
            'notification_type': 'inbox'
        })]
        self.message_post(record_name='Leave Request', body=""" Leave Request from employee: """ + employee_name + """
         <br> You can access Leave details from here: <br>""" + """<a href=%s>Link</a>""" % (
            leave_page_url)
                          , message_type="notification",
                          subtype_xmlid="mail.mt_comment",
                          author_id=self.env.user.partner_id.id,
                          notification_ids=notification_ids)


    def leave_page(self):
        menu_id = self.env.ref('hr_holidays.menu_hr_holidays_root')
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        base_url += '/web#id=%d&view_type=form&model=%s' % (self.id, self._name)
        base_url += '&menu_id=%d&action=%s' % (menu_id.id, '')
        return base_url

    def notify_with_notification(self):
        # send notification to approvers
        for leave in self:
            if leave.employee_id.parent_id and leave.employee_id.parent_id.user_id:
                approver_partner = leave.employee_id.parent_id.user_id.partner_id.id
                self.sudo().send_notification(approver_partner, leave.employee_id.name, self.sudo().leave_page())

    def notify_approvers(self):
        self.sudo().notify_with_notification()


    @api.model
    def create(self, values):
        """ Override to avoid automatic logging of creation """
        leave = super(HrLeave, self).create(values)
        leave.notify_approvers()
        return leave

