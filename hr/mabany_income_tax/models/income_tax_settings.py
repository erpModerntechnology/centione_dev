# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import logging

LOGGER = logging.getLogger(__name__)


class IncomeTaxSettings(models.Model):
    _name = 'income.tax.settings'

    name = fields.Char(string="Name", required=False, )
    line_ids = fields.One2many(comodel_name="income.tax.settings.line", inverse_name="income_tax_id",
                               string="Taxes Divisions", required=False, ondelete='cascade')
    is_functional_exempt = fields.Boolean(string="Function Exemption")
    functional_exempt_value = fields.Float(string="Functional Exemption Value", required=False, digits=(12, 6))
    class_ids = fields.One2many('income.tax.class', inverse_name='income_tax_id', string='Taxes Classes',
                                ondelete='cascade')

    def get_old_tax_gross(self, payslip):
        old_payslip = self.env['hr.payslip'].search([
            ('id', '!=', payslip.id),
            ('state', 'in', ['done']),
            ('payslip_run_id', '!=', False),
            ('employee_id', '=', payslip.employee_id),
            ('date_from', '>=', payslip.date_from),
            ('date_from', '<=', payslip.date_to),
        ])
        old_tax = 0
        old_gross = 0
        if old_payslip:
            for payslip in old_payslip:
                if payslip.line_ids.filtered(lambda k: k.code == 'INCTAX'):
                    for line in payslip.line_ids:
                        if line.code == 'INCTAX':
                            old_tax += line.total
                            break
                        if line.category_id.code in ['ALW', 'DED', 'BASIC']:
                            old_gross += line.total
        return old_tax, old_gross
        # else:
        #     return 0,0

    # @api.constrains('line_ids')
    # def check_line_ids(self):
    #     if self.line_ids:
    #         prev = self.line_ids[0].max_value
    #         for line in self.line_ids[1:]:
    #             # if abs(prev - line.min_value) > 0.0001:
    #             #     raise ValidationError('Tax Division Is Missing')
    #             prev = line.max_value

    def calc_income_tax(self, tax_pool, payslip):
        old_tax, old_gross = self.get_old_tax_gross(payslip)
        tax_pool += old_gross
        income_tax_settings = self.env.ref('mabany_income_tax.income_tax_settings0')
        functional_exemption = income_tax_settings.is_functional_exempt and income_tax_settings.functional_exempt_value or 0
        if payslip.contract_id.is_part_time == True:
            effective_salary_be = tax_pool + functional_exemption + 1250
            effective_salary = effective_salary_be - functional_exemption
        else:
            effective_salary = tax_pool - functional_exemption
        income_tax = 0.0
        income_tax_after_exemption = 0.0

        starting_beginning_segment_sequence = 1

        for class_seg in income_tax_settings.class_ids:
            if class_seg.value_from <= effective_salary <= class_seg.value_to:
                starting_beginning_segment_sequence = class_seg.rank
                break

        sorted_lines = income_tax_settings.line_ids.search(
            [('beginning_segment_sequence', '>=', starting_beginning_segment_sequence)]).sorted(lambda x: x.sequence)
        for line in sorted_lines:
            if line.diff_value:
                if effective_salary <= line.diff_value:
                    income_tax += (line.tax_ratio / 100.0) * effective_salary
                    income_tax_after_exemption = (100 - line.discount_ratio) / 100.0 * income_tax
                    break
                elif effective_salary > line.diff_value:
                    effective_salary -= line.diff_value
                    income_tax += (line.tax_ratio / 100.0) * line.diff_value

            else:
                income_tax += (line.tax_ratio / 100.0) * effective_salary
                break
        return income_tax_after_exemption - old_tax

    def calc_next_tax(self, tax_pool, employee, payslip):
        previous_tax = 0
        previous_tax_pool = 0
        salary_slips = self.env['hr.payslip'].search([
            ('state', '=', 'done'),
            ('date_to', '<=', payslip.date_to),
            ('date_from', '>=', payslip.date_from),
            ('employee_id', '=', employee.id)], order='date_to desc')
        salary_slips_filtered = salary_slips.filtered(
            lambda x: 'INCTAX' in x.line_ids.mapped('code') or 'NXTTAX' in x.line_ids.mapped('code'))
        for salary_slip in salary_slips_filtered:
            for line in salary_slip.line_ids:
                if line.code in ['INCTAX', 'NXTTAX']:
                    previous_tax += abs(line.total)
                    break
                elif line.category_id.code in ['BASIC', 'ALW', 'DED']:
                    previous_tax_pool += line.total

        tax_amount = self.calc_income_tax(tax_pool + previous_tax_pool) - previous_tax
        return tax_amount

    def get_attendance_rate(self, payslip, contract):
        no_of_days = (contract.date_start - payslip.date_from).days
        return no_of_days / (payslip.date_to - payslip.date_from).days

    def check_date(self, payslip, contract):
        if fields.Date.from_string(payslip.date_from).month == fields.Date.from_string(
                contract.date_start).month and fields.Date.from_string(
            payslip.date_from).year == fields.Date.from_string(contract.date_start).year:
            return True
        return False


class IncomeTaxSettingsLine(models.Model):
    _name = 'income.tax.settings.line'
    _order = 'min_value asc'

    income_tax_id = fields.Many2one(comodel_name="income.tax.settings", string="Income Tax Settings", required=False, )
    max_value = fields.Float(string="Maximum Value", required=False, digits=(12, 6))
    diff_value = fields.Float(string="Difference Value", required=False, compute='compute_diff_value', digits=(12, 6))
    tax_ratio = fields.Float(string="Tax Ratio %", required=False, digits=(12, 6))
    discount_ratio = fields.Float(string="Discount Ratio %", required=False, digits=(12, 6))

    sequence = fields.Integer(string="Sequence", required=False)
    min_value = fields.Float(string="Minimum Value", required=False, digits=(12, 6))

    beginning_segment_sequence = fields.Integer(default=1)

    @api.depends('max_value', 'max_value')
    def compute_diff_value(self):
        for rec in self:
            if rec.max_value:
                rec.diff_value = rec.max_value - rec.min_value
            else:
                rec.diff_value = 0

    @api.constrains('max_value', 'max_value', 'discount_ratio', 'tax_ratio')
    def check_all_values(self):
        if self.max_value and self.min_value and self.max_value < self.min_value:
            raise ValidationError('Minimum Value Can not be greater than maximum value')
        if self.tax_ratio < 0 or self.tax_ratio > 100:
            raise ValidationError('Tax Ratio Must Be Between 0 and 100')
        if self.discount_ratio < 0 or self.discount_ratio > 100:
            raise ValidationError('Discount Ratio Must Be Between 0 and 100')


class IncomeTaxClass(models.Model):
    _name = 'income.tax.class'

    income_tax_id = fields.Many2one(comodel_name="income.tax.settings", string="Income Tax Settings", required=False, )
    value_from = fields.Float(string='From')
    value_to = fields.Float(string='To')
    rank = fields.Integer(string='Rank')
