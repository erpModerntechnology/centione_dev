from odoo import models, fields, api, _


class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'


    def compute_sheet(self):
        self=self.sudo()

        return super(HrPayslipEmployees, self).compute_sheet()


