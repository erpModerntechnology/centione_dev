# -*- coding: utf-8 -*-

from odoo import models, fields, api

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class VariableAllowanceDeductionType(models.Model):
    _inherit = 'hr.variable.allowance.deduction.type'


    def create_salary_rule(self):
        if not self.salary_rule_id:
            if self.type == 'allowance':
                data = {
                    'name': "%s salary rule" % self.name,
                    'code': self.code,
                    'category_id': self.env.ref('hr_payroll.ALW').id,
                    'sequence': 5,
                    'amount_select': 'code',
                    'amount_python_compute': 'result = inputs.%s.amount' % self.code,
                    'condition_select': 'python',
                    'condition_python': 'result = inputs.%s' % self.code,
                    'struct_id': self.env.ref('mabany_hr_payroll_base.custom_default_payroll_structure').id
                }
            elif self.type == 'deduction':
                data = {
                    'name': "%s salary rule" % self.name,
                    'code': self.code,
                    'category_id': self.env.ref('hr_payroll.DED').id,
                    'sequence': 5,
                    'amount_select': 'code',
                    'amount_python_compute': 'result = - inputs.%s.amount' % self.code,
                    'condition_select': 'python',
                    'condition_python': 'result = inputs.%s' % self.code,
                    'struct_id': self.env.ref('mabany_hr_payroll_base.custom_default_payroll_structure').id
                }

            self.salary_rule_id = self.env['hr.salary.rule'].create(data)
            self.payslip_input_type_id = self.env['hr.payslip.input.type'].create(
                {'name': self.name, 'code': self.code})

        else:
            raise UserError(_('Salary rule is already created before ( %s )') % self.salary_rule_id.name)
