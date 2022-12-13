from odoo import fields, models, api
import xlsxwriter
from io import BytesIO
import base64


class InvHoldingTaxesReportWiz(models.TransientModel):
    _name = 'invoice.holding.taxes.report.wiz'
    _description = 'Invoice with Holding Taxes Report'

    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)

    gentextfile = fields.Binary('Click On Save As Button To Download File', readonly=True)

    def generate_report(self):
        # first_id = self.ids[0]
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Invoice With Tax Report')
        sheet.right_to_left()
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

        sheet.set_column(0, 13, 15)
        headers = ['مسلسل', 'رقم التسجيل الضريبي', 'الرقم القومي', 'إسم الممول', 'العنوان',
                   'إسم المأمورية',
                   'تاريخ التعامل', 'القيمة الإجمالية للتعامل', 'تاريخ التعامل للمبلغ المخصوم',
                   'القيمة الصافية للتعامل',
                   'نسبة الخصم', 'المحصل لحساب الضريبة']

        invoices = self.env['account.move'].search(
            [('invoice_date', '>=', self.date_from), ('invoice_date', '<=', self.date_to),
             ('move_type', 'in', ['in_invoice', 'in_refund'])])

        col = 0
        row = 0
        for header in headers:
            sheet.write(row, col, header, header_format)
            col += 1
        row += 1
        total_add_amount = 0
        total_subtotal = 0
        total_holding_taxes = 0
        for rec in invoices:
            with_holding_tax = False
            with_holding_tax_amount = 0
            total_tax_amount = 0
            for tax in rec.taxes_ids:
                if tax.with_holding_tax is True:
                    with_holding_tax = True
                    with_holding_tax_amount += tax.amount
            for line in rec.invoice_line_ids:
                total_tax_amount += with_holding_tax_amount/100 * line.price_subtotal
            if with_holding_tax is True:
                # 1
                col = 0
                sheet.write(row, col, rec.name, cell_format)
                # 2
                col += 1
                sheet.write(row, col, rec.partner_id.vat or '-', cell_format)
                # 3
                col += 1
                sheet.write(row, col, rec.partner_id.national_id or '-', cell_format)
                # 4
                col += 1
                sheet.write(row, col, rec.partner_id.name or '-', cell_format)
                # 5
                col += 1
                sheet.write(row, col, rec.partner_id.street or '-', cell_format)
                # 6
                col += 1
                sheet.write(row, col, rec.errand_id.name or '-', cell_format)
                # 7
                col += 1
                sheet.write(row, col, str(rec.invoice_date) or '-', cell_format)
                # 8
                col += 1
                # add_amount = (with_holding_tax_amount / 100 * with_holding_tax_amount) + line.price_subtotal
                if rec.move_type == 'in_invoice':
                    sheet.write(row, col, rec.amount_total, cell_format)
                    total_add_amount += rec.amount_total
                else:
                    sheet.write(row, col, -rec.amount_total, cell_format)
                    total_add_amount += -rec.amount_total

                # 9
                col += 1
                sheet.write(row, col, str(rec.invoice_date) or '-', cell_format)
                # 10
                col += 1
                # subtotal = line.price_unit * line.quantity
                if rec.move_type == 'in_invoice':
                    sheet.write(row, col, rec.amount_untaxed, cell_format)
                    total_subtotal += rec.amount_untaxed
                else:
                    sheet.write(row, col, -rec.amount_untaxed, cell_format)
                    total_subtotal += -rec.amount_untaxed
                # 11
                col += 1
                sheet.write(row, col, str(abs(with_holding_tax_amount)) + '%' or '-', cell_format)
                # 12
                col += 1
                sheet.write(row, col, abs(total_tax_amount), cell_format)
                total_holding_taxes += total_tax_amount
                row += 1
                sheet.set_row(row, 20)
        row += 1
        sheet.write(row, 6, 'الإجمالي', total_line_format)
        sheet.write(row, 7,total_add_amount , cell_format)
        sheet.write(row, 9, total_subtotal, cell_format)
        sheet.write(row, 11, abs(total_holding_taxes), cell_format)

        workbook.close()
        output.seek(0)
        self.write({'gentextfile': base64.encodestring(output.getvalue())})
        return {
            'type': 'ir.actions.act_url',
            'name': 'Invoice Taxes Report',
            'url': '/web/content/invoice.holding.taxes.report.wiz/%s/gentextfile/Taxes Report.xlsx?download=true' % (
                self.id),
            'target': 'new'
        }