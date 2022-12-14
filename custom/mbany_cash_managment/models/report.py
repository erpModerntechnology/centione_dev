from odoo import models, fields, api
from odoo.exceptions import ValidationError
import xlsxwriter
from io import BytesIO
import base64
from datetime import timedelta


class ItemCardWizard(models.TransientModel):
    _name = 'git.cgit'
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    gentextfile = fields.Binary('Click On Save As Button To Download File', readonly=True)

    def generate_report(self):
        print('ooooooooooooooooooooooo')
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Cash Management Report')
        # sheet.right_to_left()
        # formats
        header_format = workbook.add_format({
            'bold': 1,
            'border': 2,
            'bg_color': '#AAB7B8',
            'font_size': '10',
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
        })
        super_format = workbook.add_format({
            'bold': 2,
            'border': 2,
            'bg_color': '#AAB7B8',
            'font_size': '30',
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
        })
        cell_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
        })
        total_line_format = workbook.add_format({
            'bg_color': '#afd095',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
        })
        row = 7
        col = 10
        sheet.merge_range('B2:D3', 'Mabany Edris', super_format)
        sheet.merge_range('F3:H3', str(fields.Datetime.now() + timedelta(hours=2)), cell_format)
        sheet.merge_range(5, 0, 6, 0, 'Date', header_format)
        sheet.merge_range(5, 1, 6, 1, 'Vendor', header_format)
        sheet.merge_range(5, 2, 6, 2, 'Item', header_format)
        sheet.merge_range(5, 3, 6, 3, 'Descripition', header_format)
        sheet.merge_range(5, 4, 6, 4, 'Project', header_format)
        sheet.merge_range(5, 5, 6, 5, 'Reference', header_format)
        sheet.merge_range(5, 6, 6, 6, 'Amount', header_format)
        sheet.merge_range(5, 7, 6, 7, 'Amount Paid', header_format)
        sheet.merge_range(5, 8, 6, 8, 'Due', header_format)
        sheet.merge_range(5, 9, 6, 9, 'journal', header_format)
        sheet.set_column(0, 0, 15)
        sheet.set_column(1, 1, 25)
        sheet.set_column(3, 3, 50)
        sheet.set_column(4, 4, 15)
        sheet.set_column(2, 2, 15)
        sheet.set_column(5, 5, 15)
        sheet.set_column(6, 6, 15)
        sheet.set_column(7, 7, 15)
        sheet.set_column(9, 9, 15)
        domain = [('diff_amount','>',0),('approved','=',True)]
        if self.date_from:
            domain.append(('move_id.invoice_date','>=',self.date_from))
        if self.date_to:
            domain.append(('move_id.invoice_date','<=',self.date_to))


        git = self.env['account.move.line'].search(domain)


        for r in git:
            sheet.write(row, 0,str(r.move_id.invoice_date) or '', cell_format)
            sheet.write(row, 1,r.move_id.partner_id.name or '', cell_format)
            sheet.write(row, 2,r.product_id.display_name or '', cell_format)
            sheet.write(row, 3,r.name or '', cell_format)
            sheet.write(row, 4,r.analytic_account_id.name or '', cell_format)
            sheet.write(row, 5,r.move_id.name or '', cell_format)
            sheet.write(row, 6,r.price_total, cell_format)
            sheet.write(row, 7,r.price_total - r.diff_amount, cell_format)
            sheet.write(row, 8,r.diff_amount, cell_format)
            sheet.write(row, 9,r.approve_journal_id.name or '', cell_format)
            row += 1

        workbook.close()
        output.seek(0)
        self.write({'gentextfile': base64.encodestring(output.getvalue())})
        return {
            'type': 'ir.actions.act_url',
            'name': 'Cash Management Report',
            'url': '/web/content/git.cgit/%s/gentextfile/Cash Management Report.xlsx?download=true' % (
                self.id),
            'target': 'current'
        }
