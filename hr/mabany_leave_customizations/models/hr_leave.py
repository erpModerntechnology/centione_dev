# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError



class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    holiday_type = fields.Selection([('marriage','جواز'),('casual','عارضة'),('sick','مرضى')])
    exception_constraint = fields.Boolean('Exception Constraint')


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    exception_constraint = fields.Boolean('Exception Constraint')

    @api.constrains('number_of_days')
    def constraint_number_of_days_casual(self):
        total_dur_casual = []
        total_dur_marriage = []
        leave = self.env['hr.leave'].search([])
        for rec in leave:
            if self.employee_id.id == rec.employee_id.id:
                if self.holiday_status_id.holiday_type == 'casual':
                    if rec.exception_constraint == False:
                        if rec.request_date_from.month == self.request_date_to.month:
                            total_dur_casual.append(rec.number_of_days)
                if rec.holiday_status_id.holiday_type == 'marriage':
                        total_dur_marriage.append(rec.number_of_days)
                        if sum(total_dur_marriage) > 7:
                            raise ValidationError(_("Marriage Holiday must not exceeds a week maximum"))
                        # if rec.request_date_from.month != rec.request_date_to.month:
                        #         raise ValidationError(_("Casual Holiday must not be in 2 separate months"))
        if sum(total_dur_casual) > 2:
            raise ValidationError(_("Casual Holiday must not exceeds 2 days per month"))



    # @api.constrains('number_of_days')
    # def constraint_number_of_days_marriage(self):
    #     leave = self.env['hr.leave'].search([])
    #     total_dur = []
    #     for rec in leave:
    #         if self.employee_id.id == rec.employee_id.id:


    