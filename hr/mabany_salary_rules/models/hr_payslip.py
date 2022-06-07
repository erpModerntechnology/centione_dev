from odoo import models, fields, api



class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.onchange('employee_id')
    def get_terminated_contract(self):
        terminated = []
        contract = self.env['hr.contract'].search([('employee_id','=',self.employee_id.id),('state','=','cancel')])
        if contract:
            terminated.append(contract.id)
            convert_to_str = [str(rec.id) for rec in contract]
            fully = "".join(convert_to_str)
            self.contract_id = int(fully)

        lost = self.env['hr.payslip'].search([('id', '!=', self._origin.id)])
        if lost:
            for rec in lost:
                if contract:
                    if rec.employee_id == contract.employee_id:
                            self.contract_id = None

