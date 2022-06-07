from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HrContract(models.Model):
    _inherit = 'hr.contract'
    
    @api.model
    def create(self,vals):
        res = super(HrContract, self).create(vals)
        emp = self.env['hr.employee'].search([('id','=',vals['employee_id'])],limit=1)
        if emp.hire_date:
            date = emp.hire_date.year + 1
            combined_end = str(date) + '-' + str(emp.hire_date.month) + '-' + str(emp.hire_date.day)
            combined_start = str(emp.hire_date.year) + '-' + str(emp.hire_date.month) + '-' + str(emp.hire_date.day)
            res.date_end = datetime.strptime(combined_end, '%Y-%m-%d').date()
            res.date_start = datetime.strptime(combined_start, '%Y-%m-%d').date()
            emp.first_contract_date = datetime.strptime(combined_start, '%Y-%m-%d').date()
        return res


    @api.onchange('department_id')
    def get_hr_dep(self):
        return {'domain':{'hr_responsible_id':[('department_id','=',self.department_id.id)]}}

    hr_responsible_id = fields.Many2one('res.users', 'HR Responsible', tracking=True,
                                        help='Person responsible for validating the employee\'s contracts.')