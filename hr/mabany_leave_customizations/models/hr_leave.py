# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    holiday_type = fields.Selection(
        [('marriage', 'جواز'), ('casual', 'عارضة'), ('sick', 'مرضى'), ('unpaid', 'غير مدفوع')])
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
            if sum(total_dur_marriage) > 7:
                raise ValidationError(_("Marriage Holiday must not exceeds a week maximum"))
