from odoo import models, fields, api, _


class HrMedicalInsuranceLines(models.Model):
    _name = 'hr.medical.insurance.lines'

    medical_id = fields.Many2one('hr.medical.insurance')
    grade_id = fields.Many2one('hr.grade')
    name = fields.Char(related='grade_id.name', store=True)
    subscription = fields.Float()
    company_share = fields.Float()
    company_share_percentage = fields.Boolean()
    employee_share = fields.Float()
    employee_share_percentage = fields.Boolean()
    fees = fields.Float()
    fees_percentage = fields.Boolean()
    tax = fields.Float()
    tax_percentage = fields.Boolean()
    total_employee_share = fields.Float(compute='_compute_total_employee_share', store=True)


    @api.depends('employee_share', 'employee_share_percentage',
                 'fees', 'fees_percentage',
                 'tax', 'tax_percentage',
                 'subscription')
    def _compute_total_employee_share(self):
        employee_share = (self.employee_share/100) * self.subscription if self.employee_share_percentage else self.employee_share
        fees = (self.fees/100) * self.subscription if self.fees_percentage else self.fees
        tax = (self.tax/100) * self.subscription if self.tax_percentage else self.tax
        self.total_employee_share = employee_share + fees + tax

    def get_company_share(self):
        if not self.company_share_percentage:
            return self.company_share

        return (self.company_share / 100.0) * self.subscription
