from odoo import fields, models, api, _
import xlsxwriter
from io import BytesIO
import base64
from datetime import datetime
from odoo import exceptions


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    report = fields.Binary(string='Download', readonly=True)
    report_name = fields.Char()

    def action_draft(self):
        self.state = 'draft'
        for rec in self.slip_ids:
            rec.state = 'draft'


    def employee_fields(self):
        # { 'key': ('column_order', 'column_name') }
        employee_fields = {
            'name': ('0', 'Name'),
            'gender': ('1', 'Gender')
        }

        return employee_fields

    def _fetch_data(self):
        data = []
        employee_fields = self.employee_fields()

        for payslip in self.slip_ids:
            row = {}
            employee_contract = self.env['hr.contract'].search([
                ('employee_id', '=', payslip.employee_id.id),
                ('state', '=', 'open')])

            for idx, field in enumerate(employee_fields):
                object = payslip.employee_id
                names = field.split('.')

                for name in names:
                    object = getattr(object, name, 'NULL')

                value = object if object else 'NULL'
                row.update({'%s_%s' % (employee_fields[field][0], employee_fields[field][1]): value})
            row.update({'0_Employee Code': employee_contract.employee_id.zk_emp_id})
            row.update({'0_Employee Position': employee_contract.employee_id.department_id.name})
            row.update({'0_Employee Department': employee_contract.employee_id.job_id.name})

            salary_rules = {}
            for line in payslip.line_ids:
                salary_rules.update({str(line.salary_rule_id.id): line.amount})

            row.update({'salary_rules': salary_rules})
            data.append(row)

        return data

    def generate_excel(self):
        """
        Create report and export it into excel file.

        TODO improve loops complexities, try avoid using ORM and use RAW SQL instead to improve performance.
        """

        salary_rules = self.env['hr.salary.rule'].search([])

        # :labels: Contains all salary rules defined in the system.
        labels = {}
        for sal in salary_rules:
            labels.update({str(sal.id): {'name': sal.name, 'code': sal.code, 'sequence': sal.new_seq + 100}})

        # :data: List of rows of the report.
        data = self._fetch_data()
        if len(data)<1:
            raise exceptions.ValidationError(_('No Payslips in Batch.'))
        # :result: key -> Column name, value -> Column's rows.
        result = {}
        for key in data[0]:
            if not key == 'salary_rules':
                result.update({key: ['NULL'] * len(data)})
        for l in labels:
            result.update({l: ['NULL'] * len(data)})

        for idx, row in enumerate(data):
            for key in row:
                if key == 'salary_rules':
                    for k in row[key]:
                        if k in labels:
                            result[k][idx] = row[key][k]
                else:
                    result[key][idx] = row[key]

        # :new_result: Changed :result columns names.
        new_result = {}

        for key in result:
            if key in labels:
                new_result.update({'%s_%s' % (labels[key]['sequence'], labels[key]['name']): result[key]})
            else:
                new_result.update({key: result[key]})

        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        font_size_10 = workbook.add_format(
            {'font_name': 'KacstBook', 'font_size': 10, 'align': 'center', 'valign': 'vcenter',  # 'text_wrap': True,
             'border': 1})

        table_header_formate = workbook.add_format({
            'bold': 1,
            'border': 1,
            'bg_color': '#AAB7B8',
            'font_size': '10',
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True
        })

        sheet = workbook.add_worksheet('Payslips Report')
        sheet.set_column(0, len(new_result), 40)
        sheet.set_row(0, 20)

        # Writing to the excel sheet.
        ordered_keys = sorted([(int(it.split('_')[0]), it) for it in new_result.keys()], key=lambda x: x[0])
        for idx, key in enumerate(ordered_keys):
            sheet.write(0, idx, key[1].split('_')[1] if len(key[1].split('_')) > 1 else key[1], table_header_formate)
            for row_idx in range(1, len(data) + 1):
                sheet.write(row_idx, idx, new_result[key[1]][row_idx - 1], font_size_10)

        workbook.close()
        output.seek(0)
        self.report = base64.encodestring(output.read())
        self.report_name = 'payslips' + str(datetime.today().strftime('%Y-%m-%d')) + '.xlsx'

        # return {
        #     "type": "ir.actions.do_nothing",
        # }


