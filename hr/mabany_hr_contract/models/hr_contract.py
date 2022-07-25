from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrContract(models.Model):
    _inherit = 'hr.contract'

    num_working_days_month = fields.Integer(default=30,
                                            help="Used as standard rate for overtime calculations regardless "
                                                 "the true working days")
    num_working_hours_day = fields.Integer(default=8,
                                           help="Used as standard rate for overtime calculations regardless "
                                                "the true working hours")
    other_earning = fields.Float('Other Earning')
    house_allowance = fields.Float('House Allowance')
    parking_allowance = fields.Float('Parking Deduction')
    mobile_allowance = fields.Float('Mobile Allowance')
    work_nature_allowance = fields.Float('Work Nature Allowance')
    profit_share = fields.Float('Profit Share')
    variable = fields.Float('variable')
    purchase_of_ins_period_refund = fields.Float('Purchase of Ins. Period Refund')
    other_deduction = fields.Float('Other Deduction')
    is_part_time = fields.Boolean('Part Time')

    @api.constrains('state')
    def constrain_state(self):
        employee_contracts = self.env['hr.contract'].search(
            [('employee_id', '=', self.employee_id.id), ('state', '=', 'open')])
        if len(employee_contracts) > 1:
            error_message = "Multiple running contracts for employee: " + str(self.employee_id.name)
            raise UserError(error_message)
