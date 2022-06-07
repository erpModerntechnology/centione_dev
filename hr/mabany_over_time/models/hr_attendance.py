from odoo import fields, models, api, _
from datetime import datetime, timedelta


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    over_time_id = fields.Many2one('over.time')


    def day_is_public_holiday(self,day_date):
        found_public_holiday = self.env['hr.holidays.public.line'].sudo().search([(
            'date', '=', day_date
        )])
        if found_public_holiday:
            return True
        else:
            return False

    @api.constrains('check_in', 'check_out')
    def overtime_requester(self):
        for res in self:
            if res.check_in and res.check_out and res.employee_id.automatic_overtime:
                employee = res.employee_id
                check_in_date = datetime.strptime(str(res.check_in), '%Y-%m-%d %H:%M:%S').date()
                check_in_day = str((int(datetime.strftime(check_in_date, '%w')) - 1) % 7)
                schedule_days = [it.dayofweek for it in employee.resource_calendar_id.attendance_ids]

                if check_in_day not in schedule_days or self.day_is_public_holiday(check_in_date):
                    data = {
                        'date_from': res.check_in,
                        'date_to': res.check_out,
                        'employee_id': res.employee_id.id,
                        'holiday_type': 'holiday',
                        'attendance_id': res.id,
                    }
                    if res.over_time_id:
                        res.over_time_id.write(data)
                    else:
                        res.over_time_id = self.env['over.time'].create(data)

                else:
                    schedule_check_in_time = schedule_check_out_time = ''

                    for it in employee.resource_calendar_id.attendance_ids:
                        if it.dayofweek == check_in_day:
                            schedule_check_in_time = it.hour_from
                            schedule_check_out_time = it.hour_to

                    if schedule_check_in_time and schedule_check_out_time:
                        schedule_working_hours = schedule_check_out_time - schedule_check_in_time
                        worked_hours = (res.check_out - res.check_in).total_seconds() / 3600
                        if worked_hours > schedule_working_hours:
                            time_diff = worked_hours - schedule_working_hours
                            data = {
                                'employee_id': employee.id,
                                'date_from': res.check_out - timedelta(hours=time_diff),
                                'date_to': res.check_out,
                                'holiday_type': 'schedule_day',
                                'attendance_id': res.id,
                            }

                            if res.over_time_id:
                                res.over_time_id.write(data)
                            else:
                                res.over_time_id = self.env['over.time'].create(data)



