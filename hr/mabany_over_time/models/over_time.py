# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from datetime import datetime, timedelta
import math


class OverTime(models.Model):
    _name = 'over.time'

    name = fields.Char(string="Name", required=False, )
    date_from = fields.Datetime(string="Date From")
    date_to = fields.Datetime(string="Date To")
    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee", required=False, )
    state = fields.Selection(string="", selection=[('draft', 'Draft'), ('approved', 'Approved'), ('done', 'Done')],
                             default='draft')
    company_id = fields.Many2one(comodel_name="res.company")
    holiday_type = fields.Selection([('holiday', 'Holiday'),
                                     ('schedule_day', 'Working Day')])

    morning_hours = fields.Float(compute='_compute_hours', store=True)
    night_hours = fields.Float(compute='_compute_hours', store=True)
    holiday_hours = fields.Float(compute='_compute_hours', store=True)
    total_hours = fields.Float(compute='_compute_hours', store=True)

    attendance_id = fields.Many2one('hr.attendance')
    payslip_id = fields.Many2one('hr.payslip')

    def _get_morning_night_hours(self, date_from, date_to, morning_start_hour):
        # TODO: Refactor and clean the code.
        day_zero_str = "1970-01-01 %s:00:00" % morning_start_hour
        day_zero = datetime.strptime(day_zero_str, '%Y-%m-%d %H:%M:%S')

        time_diff = (date_to - date_from).total_seconds() / 86400 * 2

        mapped_from = (date_from - day_zero).total_seconds() / 86400 * 2
        mapped_to = (date_to - day_zero).total_seconds() / 86400 * 2

        from_ceil = math.ceil(mapped_from)
        from_floor = math.floor(mapped_from)
        to_floor = math.floor(mapped_to)

        morning = 0
        night = 0

        start_morning = False
        end_morning = False

        if from_floor % 2 == 0:  # even
            start_morning = True

        if to_floor % 2 == 0:  # even
            end_morning = True

        if from_floor == to_floor:
            if start_morning:  # morning
                morning = time_diff
            else:
                night = time_diff
        else:
            if start_morning:
                morning += (from_ceil - mapped_from)
            else:
                night += (from_ceil - mapped_from)

            time_diff -= (from_ceil - mapped_from)

            if end_morning:
                morning += (mapped_to - to_floor)
            else:
                night += (mapped_to - to_floor)

            time_diff -= (mapped_to - to_floor)

            if time_diff:
                diff = to_floor - from_ceil
                if diff >= 2:
                    morning += ((diff - (diff % 2)) / 2)
                    night += ((diff - (diff % 2)) / 2)
                    diff = diff % 2

                if diff:
                    if from_ceil % 2 == 0 and to_floor % 2 != 0:
                        morning += diff
                    elif from_ceil % 2 != 0 and to_floor % 2 == 0:
                        night += diff

        return {
                'morning_hours': (morning * 24) / 2,
                'night_hours': (night * 24) / 2
        }

    @api.depends('date_from', 'date_to', 'holiday_type')
    def _compute_hours(self):
        for rec in self:
            if rec.date_from and rec.date_to:

                if rec.holiday_type == 'holiday':
                    rec.morning_hours = rec.night_hours = 0
                    rec.holiday_hours = (rec.date_to - rec.date_from).total_seconds() / 3600

                else:
                    morning_start_hour = str(self.env['ir.config_parameter'].get_param('morning_start_hour', default=5)) or "05"
                    # TODO: resolve hardcoded time zone +2.
                    date_from = datetime.strptime(str(rec.date_from), '%Y-%m-%d %H:%M:%S') + timedelta(hours=2)
                    date_to = datetime.strptime(str(rec.date_to), '%Y-%m-%d %H:%M:%S') + timedelta(hours=2)

                    morning_night_hours = self._get_morning_night_hours(date_from, date_to, morning_start_hour)

                    rec.morning_hours = morning_night_hours['morning_hours']
                    rec.night_hours = morning_night_hours['night_hours']
                    rec.holiday_hours = 0

                rec.total_hours = rec.morning_hours + rec.night_hours + rec.holiday_hours

    def migrate_company(self):
        records = self.search([])
        for p in records:
            p.company_id = p.employee_id.company_id.id

    @api.onchange('employee_id')
    def onchange_employee(self):
        self.update({
            'company_id': self.employee_id.company_id.id
        })

    @api.model
    def create(self, vals):
        seq_val=self.env['ir.sequence'].next_by_code('over.time')
        if seq_val:
            vals['name'] = seq_val

        if 'employee_id' in vals:
            employee = self.env['hr.employee'].browse(vals['employee_id'])
            vals['company_id'] = employee.company_id.id
        return super(OverTime, self).create(vals)

    def action_done(self):
        for rec in self:
            rec.write({'state': 'done'})

    def action_approve(self):
        for rec in self:
            rec.write({'state': 'approved'})
