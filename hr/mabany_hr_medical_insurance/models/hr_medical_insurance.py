from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

from io import BytesIO
import xlsxwriter
import base64
from datetime import datetime


class HrMedicalInsurance(models.Model):
    _name = 'hr.medical.insurance'

    name = fields.Char()
    insurance_company_id = fields.Many2one('hr.insurance.company')
    max_allowed_grades = fields.Integer()
    line_ids = fields.One2many('hr.medical.insurance.lines', 'medical_id')
    max_number_subscribers = fields.Integer()
    number_of_subscribers = fields.Integer(compute='_compute_number_of_subscribers', store=True)
    subscribers_ids = fields.One2many('hr.employee.medical.line', 'medical_id')
    date_from = fields.Date()
    date_to = fields.Date()
    critical_case_allowance = fields.Float()
    state = fields.Selection([('draft', 'Draft'), ('open', 'Running'),
                              ('close', 'Expired'), ('cancel', 'Cancelled')], default='draft')

    report = fields.Binary(string='Download', readonly=True)
    report_name = fields.Char()


    @api.constrains('line_ids')
    def _check_max_grades(self):
        if len(self.line_ids) > self.max_allowed_grades:
            raise ValidationError("Exceeded Max allowed grades!!")


    @api.depends('subscribers_ids')
    def _compute_number_of_subscribers(self):
        self.number_of_subscribers = len(self.subscribers_ids) + sum([len(sub.follower_ids)
                                                                      for sub in [sub for sub in self.subscribers_ids]])
        if self.number_of_subscribers > self.max_number_subscribers:
            raise ValidationError("Exceeded Max allowed subscribers for this Medical Contract")

    def subscribers_report(self):
        header, data = self._fetch_data()
        self._write_report(header, data, 'Medical Care report')

    def _fetch_data(self):
        header = ['Attendance ID', 'Name', 'Medical Grade', 'Company Share', 'Company Share percentage?',
                  'Employee Share', 'Employee Share percentage?', 'Cost', 'Followers']
        data = []

        for subscriber in self.subscribers_ids:
            row = []

            attendance_id = getattr(subscriber.employee_id, 'attendance_id', 'NULL')
            row.append(attendance_id if attendance_id else 'NULL')

            name = getattr(subscriber.employee_id, 'name', 'NULL')
            row.append(name if name else name)

            row.append(subscriber.medical_grade_id.name)
            row.append(subscriber.medical_grade_id.company_share)

            company_share_percentage = subscriber.medical_grade_id.company_share_percentage
            row.append('Yes' if company_share_percentage else 'No')

            row.append(subscriber.medical_grade_id.total_employee_share)

            employee_share_percentage = subscriber.medical_grade_id.employee_share_percentage
            row.append('Yes' if employee_share_percentage else 'No')

            row.append(subscriber.cost / 12.0)
            row.append(len(subscriber.follower_ids))

            data.append(row)

        return header, data

    def _write_report(self, header, data, name):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet(name)

        for idx, head in enumerate(header):
            sheet.write(0, idx, head)

        for row_idx, row in enumerate(data):
            for col_idx, col in enumerate(row):
                sheet.write(row_idx+1, col_idx, col)

        workbook.close()
        output.seek(0)
        self.report = base64.encodestring(output.read())
        self.report_name = name + str(datetime.today().strftime('%Y-%m-%d')) + '.xlsx'