from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError

from datetime import datetime,timedelta
import calendar


class HrExcuse(models.Model):
    _inherit = 'hr.excuse'


    # @api.constrains('start_date', 'end_date')
    # def _check_date(self):
    #     max_period = self.employee_id.max_excuse_period
    #     excuses_this_month = self.env['hr.excuse'].search([('employee_id', '=', self.employee_id.id)])
    #     total = 0
    #     for rec in excuses_this_month:
    #         total += rec.period
    #         if total > max_period:
    #             raise UserError(_('Period exceeds employee\'s allowed period .'))
