# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, timedelta


class hr_attendance_inherit(models.Model):
    _inherit = 'hr.attendance'

    def is_absent(self, employee, date):
        # if employee shcudle is open and hours=0 not to ab absent
        # or if: contract start date is after this comming day date, then not absent
        if (employee.resource_calendar_id and employee.resource_calendar_id.schedule_type == 'open' and employee.resource_calendar_id.hours_per_day == 0) or (
                (employee.contract_id.date_start > date) if employee.contract_id.date_start else (1==5)):
            return False
        #if employee has a mission,not to be absent
        missions = self.env['hr.mission'].search([('employee_id', '=', employee.id),
                                                  ('state','=','validate'),

                                                  ])
        for mission in missions:
            if mission.start_date.date() <= date <= mission.end_date.date():
                # if (mission.end_date - mission.start_date).total_seconds() / 3600.0 >= 24:
                return False

        else:
            return super(hr_attendance_inherit, self).is_absent(employee, date)

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
