from odoo import fields, api, models, _
from odoo import exceptions

from datetime import datetime, time

from dateutil import rrule

class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    contract_valid_based = fields.Boolean(default=False,help="If this field is set the salary rule rate will be affected by the start and end dates of the contract.")

class HrContract(models.Model):
    _inherit = 'hr.contract'

    def get_work_ratio(self,date_from,date_to):

        salary_start = max(self.date_start,date_from)
        salary_end = min(self.date_end,date_to) if self.date_end else date_to

        # This the case of normal payslip (month does not contain join date or contract end )
        # if salary_start == date_from and salary_end == date_to:
        #     return 1

        salary_start_datetime = fields.Datetime.from_string(salary_start)
        salary_end_datetime = fields.Datetime.from_string(salary_end)
        month_days_count = 30
        month_end = fields.Datetime.from_string(date_to)
        month_start = fields.Datetime.from_string(date_from)

        payslip_days = (month_end - month_start).days + 1

        # The case of month contain contract end i.e. employee termination or resignation
        # if salary_start == date_from:
        #     num_work_days = (salary_end_datetime - salary_start_datetime).days + 1
        #
        # # The case of month contain join date i.e. first month for an employee (new employee)
        # elif salary_end == date_to:
        #     num_work_days = (salary_end_datetime - salary_start_datetime).days + 1
        #
        #
        # # The case of employee that join and resigned on the same month
        # else:
        num_work_days = (salary_end_datetime - salary_start_datetime).days + 1

        # num_work_days = num_work_days + month_days_count - payslip_days
        print(num_work_days)
        return (1.0 * num_work_days) / (1.0 * month_days_count)

class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    def get_missing_attendance(self, contract, date_from_str, date_to_str):

        self.ensure_one()
        print('before',contract)
        contract = contract[0]
        print('after',contract)
        work_schedule = contract.employee_id.resource_calendar_id or contract.resource_calendar_id

        attendance_model = self.env['hr.attendance']
        _weekdays = work_schedule._get_weekdays()

        if _weekdays:
            weekdays = _weekdays
        else:
            raise exceptions.ValidationError(_('No valid Work Schedule found.'))

        date_from = fields.Date.from_string(date_from_str)
        date_to = fields.Date.from_string(date_to_str)

        scheduled_workdays = rrule.rrule(rrule.DAILY, dtstart=date_from, wkst=rrule.SU,
                                         until=date_to, byweekday=weekdays)

        missing_checkout = []

        for day in scheduled_workdays:
            datetime_start_str = fields.Datetime.to_string(datetime.combine(day, time(0, 0)))
            datetime_end_str = fields.Datetime.to_string(datetime.combine(day, time(23, 59, 59)))
            day_date = str(day.date())

            workday = attendance_model.search([('employee_id', '=', self.id),
                                               ('check_in', '>=', datetime_start_str),
                                               ('check_out', '<=', datetime_end_str),
                                               # ('no_checkout', '=', True)
                                               ])
            # check if there is holiday in this day, not to add the day to make deduction for it
            found_public_holiday = self.env['hr.holidays.public.line'].sudo().search([(
                'date', '=', day_date
            )])
            if found_public_holiday:
                workday = None

            # found_leave = self.env['hr.leave'].sudo().search(
            #     [('employee_id', '=', self.id), ('state', '=', 'validate')
            #         , ('start_date', '=', day_date), ('end_date', '=', day_date), ('unit_half', '=', True),
            #      ('date_from_period', '=', 'pm')], limit=1)
            # if found_leave:
            #     workday = None

            # end check

            if workday and len(workday) > 0:
                missing_checkout.append(workday)
        return (contract.work_hour_value * (contract.workday_hours / 2)) * len(set(missing_checkout))
