# -*- coding: utf-8 -*-
from datetime import datetime,date

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = "hr.employee"
    zk_emp_id = fields.Char(string="Employee Attendance ID", required=False,readonly=True)
    hire_date = fields.Date(string="Hire Date", required=False, )
    region = fields.Selection(string="Region", selection=[('muslim', 'Muslim'), ('Christian', 'Christian'), ],
                              required=False, )
    bank_name = fields.Char(string="Bank Name", required=False, )
    bank_number = fields.Char(string="Bank Account Number", required=False, )
    insurance_num = fields.Integer(string="Insurance Number", required=False, )
    insurance_start_date = fields.Date(string="Insurance Start Date", required=False, )
    insurance_office = fields.Char(string="Insurance Office", required=False, )
    private_address = fields.Char(string="العنوان", required=False, )
    bank_branch_name = fields.Char(string="Bank Branch Name")
    license_end_date = fields.Date('License End Date')
    identify_end_date = fields.Date('Identification End Date')
    passport_end_date = fields.Date('Passport End Date')

    military_status = fields.Selection(string="Military Status",
                                       selection=[('completed', 'Completed'), ('exempted', 'Exepmted'), ('postponed', 'Postponed')], required=False, )
    employee_code = fields.Char('Employee Code', required=False)
    job_grade_id = fields.Many2one('job.grade', 'Job Grade')
    payment_method = fields.Selection(string="Payment Method", selection=[('cash', 'Cash'), ('bank', 'Bank'), ],
                              required=False, )
    nbe_code = fields.Char('NBE Code', required=False)
    arabic_name = fields.Char('Arabic Name', required=False)
    job_level = fields.Many2one('job.level','Job Level')
    job_divison = fields.Many2one('job.divison','Job Divison')
    military_end_date = fields.Date('Military End Date')
    manager_job = fields.Char('Manager Position')

    _sql_constraints = [
        ('attendance_code_unique', 'unique("zk_emp_id")', 'Attendance ID Already Exists!!')
    ]


    @api.onchange('parent_id')
    def onchange_parent(self):
        for rec in self:
            if rec.parent_id.job_id:
                rec.manager_job = rec.parent_id.job_id.name


    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('zk_emp_id', operator, name)]
        return self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)

    # @api.constrains('employee_code')
    # def check_employee_code(self):
    #     employees = self.env['hr.employee'].search(
    #             [('id', '!=', self.id)])
    #     for emp in employees:
    #         if emp.employee_code == self.employee_code:
    #             raise ValidationError(_("Employee Code already existed"))

    @api.constrains('zk_emp_id')
    def check_identification_id(self):
        employees = self.env['hr.employee'].search(
            [('id', '!=', self.id)])
        for emp in employees:
            if emp.zk_emp_id == self.zk_emp_id:
                raise ValidationError(_("Attendance Id is already existed"))

    @api.constrains('identification_id')
    def check_identification_id(self):
        employees = self.env['hr.employee'].search(
            [('id', '!=', self.id)])
        for emp in employees:
            if emp.identification_id == self.identification_id:
                raise ValidationError(_("Identification Id is already existed"))

    @api.constrains('identification_id')
    def check_identification_id_length(self):
        for rec in self:
            if len(rec.identification_id) != 14:
                raise ValidationError(_("Identification Id Should Be 14 Character"))



    # @api.model
    # def create(self,vals):
    #     res = super(HrEmployee, self).create(vals)
    #     emps_values = []
    #     emps = self.env['hr.employee'].search([]).mapped('zk_emp_id')
    #     for i in emps:
    #         if i != False:
    #             if i.isdigit():
    #                 emps_values.append(int(i))
    #             else:
    #                 emps_values.append(0)
    #         else:
    #             emps_values.append(0)
    #     # emps_values = [int(i) for i in emps]
    #     maxed_emps = max(emps_values)
    #     maxed = maxed_emps + 1
    #     res.zk_emp_id = str(maxed)
    #     return res


