# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, timedelta


class hr_attendance_inherit(models.Model):
    _inherit = 'hr.attendance'

    @api.model
    def manual_recalculate_absence(self, start_date):
        date = datetime.now().date()
        # get range as  range(1 to start date)
        dates_diff = datetime.now().date() - start_date

        for day_before_ in range(1, dates_diff.days + 1):
            previous_date = date - timedelta(days=day_before_)
            # delete absence of last days
            self.env['hr.absence'].search([('date', '=', previous_date)]).unlink()

            employees = self.env['hr.employee'].search([])
            for emp in employees:
                if self.is_absent(emp, previous_date):
                    self.env['hr.absence'].create({'employee_id': emp.id, 'date': previous_date})
