# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError

from datetime import datetime
import calendar


class HrExcuse(models.Model):
    _inherit = 'hr.excuse'

    @api.constrains('period', 'employee_id', 'start_date')
    def _check_period(self):
        max_period = self.employee_id.max_excuse_period
        if self.period > max_period:
            raise UserError(_('Period exceeds employee\'s allowed period.'))
        # month = self.start_date.month
        # year = self.start_date.year
        # month_start = datetime(day=1, month=month, year=year, hour=0, minute=0, second=0)
        # month_end = datetime(day=calendar.monthrange(year, month)[1], month=month, year=year, hour=23, minute=59,
        #                      second=59)
        max_month_request = self.employee_id.number_excuse_per_month
        # excuses_this_month = self.env['hr.excuse'].search([('employee_id', '=', self.employee_id.id),
        #                                                    ('start_date', '>=', month_start),
        #                                                    ('end_date', '<=', month_end),
        #                                                    ('state', '=', 'draft')])
        # if len(excuses_this_month) > max_month_request:
        #     raise UserError(_('Period exceeds employee\'s allowed requests per month.'))
        hr_excuse_conf_line = self.env['hr.excuse.conf.lines'].search(
            [('start_date', '<=', self.start_date), ('end_date', '>=', self.start_date)], limit=1)
        if hr_excuse_conf_line:
            excuses = self.env['hr.excuse'].search([('employee_id', '=', self.employee_id.id),
                                                    ('start_date', '>=', hr_excuse_conf_line.start_date),
                                                    ('start_date', '<=', hr_excuse_conf_line.end_date),
                                                    ('state', '!=', 'refuse')])
            if len(excuses) > max_month_request:
                raise UserError(_('Period exceeds employee\'s allowed requests per interval.'))
        else:
            raise UserError(_('Excuse Start Date doesn\'t Existed in any Period'))
