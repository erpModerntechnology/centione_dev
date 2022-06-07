from odoo import models, fields, api, _

from io import BytesIO
import xlsxwriter
import base64
from datetime import datetime


class HrLifeInsurance(models.Model):
    _name = 'hr.life.insurance'

    name = fields.Char()
    insurance_company_id = fields.Many2one('hr.insurance.company')
    line_ids = fields.One2many('hr.life.insurance.lines', 'life_id')
    date_from = fields.Date()
    date_to = fields.Date()
    subscribers_ids = fields.One2many('hr.employee.life.line', 'life_id')
    state = fields.Selection([('draft', 'Draft'), ('open', 'Running'),
                              ('close', 'Expired'), ('cancel', 'Cancelled')], default='draft')

    report = fields.Binary(string='Download', readonly=True)
    report_name = fields.Char()

    def subscribers_report(self):
        header, data = self._fetch_data()
        self._write_report(header, data, 'Life insurance report')

    def _fetch_data(self):
        header = ['Attendance ID', 'Name', 'Medical Grade', 'Company Share', 'Company Share percentage?',
                  'Employee Share', 'Employee Share percentage?', 'Cost']
        data = []

        for subscriber in self.subscribers_ids:
            row = []

            attendance_id = getattr(subscriber.employee_id, 'attendance_id', 'NULL')
            row.append(attendance_id if attendance_id else 'NULL')

            name = getattr(subscriber.employee_id, 'name', 'NULL')
            row.append(name if name else name)

            row.append(subscriber.life_grade_id.name)
            row.append(subscriber.life_grade_id.company_share)

            company_share_percentage = subscriber.life_grade_id.company_share_percentage
            row.append('Yes' if company_share_percentage else 'No')

            row.append(subscriber.life_grade_id.total_employee_share)

            employee_share_percentage = subscriber.life_grade_id.employee_share_percentage
            row.append('Yes' if employee_share_percentage else 'No')

            row.append(subscriber.cost / 12.0)

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