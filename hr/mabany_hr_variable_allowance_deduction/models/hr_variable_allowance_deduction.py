from odoo import models, fields, api, _


class HrVariableAllowanceDeduction(models.Model):
    _name = 'hr.variable.allowance.deduction'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee')
    contract_id = fields.Many2one('hr.contract', compute='_get_contract_id', store=True)
    date = fields.Date()
    amount = fields.Float(compute='_set_amount', store=True)
    add_amount = fields.Float()
    type = fields.Many2one('hr.variable.allowance.deduction.type')
    payslip_id = fields.Many2one('hr.payslip')

    @api.depends('employee_id')
    def _get_contract_id(self):
        running_contracts = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id),
                                                            ('state', '=', 'open')])
        if running_contracts:
            self.contract_id = running_contracts[0].id

    @api.depends('add_amount', 'type.calculation_method', 'type.type', 'contract_id.wage')
    def _set_amount(self):
        for rec in self:
            if rec.type.type and rec.contract_id:
                if rec.type.type == 'allowance':
                    if rec.type.calculation_method == 'fixed':
                        rec.amount = rec.add_amount
                    elif rec.type.calculation_method == 'work_day':
                        rec.amount = (rec.contract_id.wage / 30.0) * rec.add_amount
                    elif rec.type.calculation_method == 'work_hour':
                        rec.amount = (rec.contract_id.wage / (30.0 * 8)) * rec.add_amount
                    else:
                        pass
                else:
                    if rec.type.calculation_method == 'fixed':
                        rec.amount = -1 * rec.add_amount
                    elif rec.type.calculation_method == 'work_day':
                        rec.amount = -1 * ((rec.contract_id.wage / 30.0) * rec.add_amount)
                    elif rec.type.calculation_method == 'work_hour':
                        rec.amount = -1 * ((rec.contract_id.wage / (30.0 * 8)) * rec.add_amount)
                    else:
                        pass
