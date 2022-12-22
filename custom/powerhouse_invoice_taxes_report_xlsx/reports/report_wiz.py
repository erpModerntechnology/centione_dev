from odoo import fields, models, api
import xlsxwriter
from io import BytesIO
import base64


class InvTaxesReportWiz(models.TransientModel):
    _name = 'invoice.taxes.report.wiz'
    _description = 'Invoice Taxes Report'

    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)

    type = fields.Selection(
        selection=[('sales_tax', 'Sales Tax'),
                   ('purchase_tax', 'Purchase Tax'), ],
        required=True, default='sales_tax')

    gentextfile = fields.Binary('Click On Save As Button To Download File', readonly=True)

    def generate_report(self):
        first_id = self.ids[0]
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Invoice Tax Report')
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
        sheet.set_column(0, 15, 15)
        sales_tax_headers = ['نوع المستند', 'رقم الفاتورة', 'إسم العميل', 'رقم التسجيل الضريبي', 'رقم الملف الضريبي',
                             'العنوان',
                             'الرقم القومي/جواز السفر', 'رقم الموبايل', 'تاريخ الفاتورة', 'فئة الضريبة',
                             'المبلغ الإجمالي', 'قيمة الخصم', 'المبلغ الصافي', 'قيمة الضريبة', 'الإجمالي']

        purchase_tax_headers = ['نوع المستند', 'رقم الفاتورة', 'إسم المورد', 'رقم التسجيل الضريبي', 'رقم الملف الضريبي',
                                'العنوان',
                                'الرقم القومي/جواز السفر', 'رقم الموبايل', 'تاريخ الفاتورة', 'فئة الضريبة',
                                'المبلغ الإجمالي', 'قيمة الخصم', 'المبلغ الصافي', 'قيمة الضريبة', 'الإجمالي']
        row = 0

        if self.type == 'sales_tax':
            self.print_sales_lines(sheet, header_format, total_line_format, cell_format, row, sales_tax_headers)

        else:
            self.print_purchase_lines(sheet, header_format, total_line_format, cell_format, row, purchase_tax_headers)

        workbook.close()
        output.seek(0)
        self.write({'gentextfile': base64.encodestring(output.getvalue())})
        return {
            'type': 'ir.actions.act_url',
            'name': 'Invoice Taxes Report',
            'url': '/web/content/invoice.taxes.report.wiz/%s/gentextfile/Taxes Report.xlsx?download=true' % (
                self.id),
            'target': 'new'
        }

    def print_sales_lines(self, sheet, header_format, total_line_format, cell_format, row, sales_tax_headers):
        sales_invoice = self.env['account.move'].search(
            [('invoice_date', '>=', self.date_from), ('invoice_date', '<=', self.date_to),
             ('move_type', 'in', ['out_invoice', 'out_refund']), ('state', '=', 'posted')])
        col = 0
        for header in sales_tax_headers:
            sheet.write(row, col, header, header_format)
            col += 1

        row += 1
        total_amount = 0
        total_disc_rec = 0
        fixed_amount = 0
        total_tax_amount = 0
        total_tax_amount_line = 0
        totals = 0
        tax = self.env['account.tax'].search(
            [('is_report', '=', True),('type_tax_use', '=', 'sale')],limit=1)
        tax_amount = 0
        for rec in sales_invoice:
            total_disc = 0
            for line in rec.line_ids:
                print("tax_totals_json :> ", line)
                if line.name == tax.name:
                    tax_amount = line.balance

            net_amount = 0
            for line_inv in rec.invoice_line_ids:
                net_amount += line_inv.quantity * line_inv.price_unit

            print("net_amount ::> ",net_amount)
            # Value_added_tax = 0
            # for tax in rec.taxes_ids:
            #     if tax.is_report is False:
            #         # with_holding_tax = True
            #         Value_added_tax += tax.amount
            # for line in rec.invoice_line_ids:
            #     total_disc += (line.discount / 100) * (line.quantity * line.price_unit)
            #     total_tax_amount_line += line.tax_base_amount
            # if Value_added_tax > 0:

            if tax_amount != 0:
                # 1
                col = 0
                sheet.write(row, col, 'فاتورة' if rec.move_type == 'out_invoice' else 'إشعار خصم',
                            cell_format)
                # 2
                col += 1
                sheet.write(row, col, rec.name, cell_format)
                # 3
                col += 1
                sheet.write(row, col, rec.partner_id.name or '-', cell_format)
                # 4
                col += 1
                sheet.write(row, col, rec.partner_id.vat or '-', cell_format)
                # 5
                col += 1
                sheet.write(row, col, rec.partner_id.tax_file_no or '-', cell_format)
                # 6
                col += 1
                sheet.write(row, col, rec.partner_id.street or '-', cell_format)
                # 7
                col += 1
                sheet.write(row, col, rec.partner_id.national_id or '-', cell_format)
                # 8
                col += 1
                sheet.write(row, col, rec.partner_id.mobile or '-', cell_format)
                # 9
                col += 1
                sheet.write(row, col, str(rec.invoice_date) or '', cell_format)
                # 10
                col += 1
                sheet.write(row, col,   '14.0 %' or '', cell_format)
                # 11
                col += 1
                sheet.write(row, col, rec.amount_untaxed if rec.move_type == 'out_invoice' else -rec.amount_untaxed,
                            cell_format)
                total_amount += rec.amount_untaxed if rec.move_type == 'out_invoice' else -rec.amount_untaxed
                # 12
                col += 1
                sheet.write(row, col, (net_amount - rec.amount_untaxed), cell_format)
                total_disc_rec += (net_amount - rec.amount_untaxed)
                # total_disc += rec.amount_total * with_holding_tax_amount / 100 if rec.move_type == 'out_invoice' else -(
                #         rec.amount_total * with_holding_tax_amount / 100)
                # 13
                col += 1
                sheet.write(row, col, net_amount if rec.move_type == 'out_invoice' else -net_amount,
                            cell_format)
                # 14
                fixed_amount += net_amount if rec.move_type == 'out_invoice' else -net_amount
                col += 1
                # tax_lines_data = rec._prepare_tax_lines_data_for_totals_from_invoice()
                # groups_by_subtotal = {
                #     **rec._get_tax_totals(rec.partner_id, tax_lines_data, rec.amount_total, rec.amount_untaxed,
                #                           rec.currency_id),
                #     'allow_tax_edition': rec.is_purchase_document(include_receipts=False) and rec.state == 'draft',
                # }
                # groups_by_subtotal = groups_by_subtotal['groups_by_subtotal']['Untaxed Amount']
                # for key in groups_by_subtotal:
                #     for key2 in key:
                #         if key2 == 'tax_group_amount':
                #             total_tax_amount_line += key[key2]
                sheet.write(row, col, -tax_amount, cell_format)
                total_tax_amount += -tax_amount
                # 15
                col += 1
                sheet.write(row, col, (net_amount + (-tax_amount)) if rec.move_type == 'out_invoice' else -(net_amount + tax_amount),
                            cell_format)
                totals += (net_amount + (-tax_amount)) if rec.move_type == 'out_invoice' else -(net_amount + tax_amount)
                row += 1
                sheet.set_row(row, 20)

        row += 1
        sheet.write(row, 9, 'الإجمالي', total_line_format)
        sheet.write(row, 10, total_amount, cell_format)
        sheet.write(row, 11, total_disc_rec, cell_format)
        sheet.write(row, 12, fixed_amount, cell_format)
        sheet.write(row, 13, total_tax_amount, cell_format)
        sheet.write(row, 14, totals, cell_format)

    def print_purchase_lines(self, sheet, header_format, total_line_format, cell_format, row, purchase_tax_headers):
        purchase_invoice = self.env['account.move'].search(
            [('invoice_date', '>=', self.date_from), ('invoice_date', '<=', self.date_to),
             ('move_type', 'in', ['in_invoice', 'in_refund'])])
        col = 0
        for header in purchase_tax_headers:
            sheet.write(row, col, header, header_format)
            col += 1

        row += 1
        total_amount = 0
        total_disc = 0
        fixed_amount = 0
        total_tax_amount = 0
        totals = 0
        tax = self.env['account.tax'].search(
            [('is_report', '=', True),('type_tax_use', '=', 'purchase')],limit=1)
        for rec in purchase_invoice:
            for line in rec.line_ids:
                print("tax_totals_json :> ", line)
                if line.name == tax.name:
                    tax_amount = line.balance

            net_amount = 0
            for line_inv in rec.invoice_line_ids:
                net_amount += line_inv.quantity * line_inv.price_unit

            print("net_amount ::> ",net_amount)
            # with_holding_tax_amount = 0
            # for tax in rec.taxes_ids:
            #     if tax.with_holding_tax is False:
            #         # with_holding_tax = True
            #         with_holding_tax_amount += tax.amount
            # for line in rec.invoice_line_ids:
            #     total_disc += line.discount
            if tax_amount != 0:
                # 1
                col = 0
                sheet.write(row, col, 'فاتورة' if rec.move_type == 'out_invoice' else 'إشعار خصم',
                            cell_format)
                # 2
                col += 1
                sheet.write(row, col, rec.name, cell_format)
                # 3
                col += 1
                sheet.write(row, col, rec.partner_id.name or '-', cell_format)
                # 4
                col += 1
                sheet.write(row, col, rec.partner_id.vat or '-', cell_format)
                # 5
                col += 1
                sheet.write(row, col, rec.partner_id.tax_file_no or '-', cell_format)
                # 6
                col += 1
                sheet.write(row, col, rec.partner_id.street or '-', cell_format)
                # 7
                col += 1
                sheet.write(row, col, rec.partner_id.national_id or '-', cell_format)
                # 8
                col += 1
                sheet.write(row, col, rec.partner_id.mobile or '-', cell_format)
                # 9
                col += 1
                sheet.write(row, col, str(rec.invoice_date) or '', cell_format)
                # 10
                col += 1
                sheet.write(row, col, '14.0 %' or '', cell_format)
                # 11
                col += 1
                sheet.write(row, col, rec.amount_untaxed if rec.move_type == 'in_invoice' else -rec.amount_untaxed,
                            cell_format)
                total_amount += rec.amount_untaxed if rec.move_type == 'in_invoice' else -rec.amount_untaxed
                # 12
                col += 1
                sheet.write(row, col, (net_amount - rec.amount_untaxed) if rec.move_type == 'in_invoice' else -(net_amount - rec.amount_untaxed), cell_format)
                total_disc += (net_amount - rec.amount_untaxed) if rec.move_type == 'in_invoice' else -(net_amount - rec.amount_untaxed)
                # 13
                col += 1
                sheet.write(row, col, net_amount if rec.move_type == 'in_invoice' else -net_amount,
                            cell_format)
                fixed_amount += net_amount if rec.move_type == 'in_invoice' else -net_amount
                # 14
                col += 1
                sheet.write(row, col, tax_amount if rec.move_type == 'in_invoice' else -tax_amount, cell_format)
                total_tax_amount += tax_amount if rec.move_type == 'in_invoice' else -tax_amount
                # 15
                col += 1
                sheet.write(row, col, (net_amount + (tax_amount)) if rec.move_type == 'in_invoice' else -(net_amount + (tax_amount)),
                            cell_format)
                totals += (net_amount + (tax_amount)) if rec.move_type == 'in_invoice' else -(net_amount + (tax_amount))
                row += 1
                sheet.set_row(row, 20)

        row += 1
        sheet.write(row, 9, 'الإجمالي', total_line_format)
        sheet.write(row, 10, total_amount, cell_format)
        sheet.write(row, 11, total_disc, cell_format)
        sheet.write(row, 12, fixed_amount, cell_format)
        sheet.write(row, 13, total_tax_amount, cell_format)
        sheet.write(row, 14, totals, cell_format)
