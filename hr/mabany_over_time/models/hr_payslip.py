from odoo import models, fields, api, _


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def create(self, vals):
        res = super(HrPayslip, self).create(vals)

        overtime_morning_rate = float(self.env['ir.config_parameter'].get_param('daily_rate', default=1)) or 1
        overtime_night_rate = float(self.env['ir.config_parameter'].get_param('night_rate', default=1)) or 1
        overtime_holiday_rate = float(self.env['ir.config_parameter'].get_param('holiday_rate', default=1)) or 1

        try:
            days_per_month = res.contract_id.__getattribute__('num_working_days_month')
        except:
            days_per_month = 30

        try:
            hours_per_day = res.contract_id.__getattribute__('num_working_hours_day')
        except:
            hours_per_day = 8

        employee_rate = res.contract_id.wage / (days_per_month * hours_per_day)

        over_time_data = self.env['over.time'].search([('state', '=', 'approved'),
                                                       ('employee_id', '=', res.employee_id.id)])
        over_time_allowance = 0

        filtered_over_time_data = []
        for it in over_time_data:
            if res.date_from <= it.date_from.date() <= res.date_to:
                filtered_over_time_data.append(it)
                if it.holiday_type == 'holiday':
                    over_time_allowance += (it.holiday_hours * employee_rate * overtime_holiday_rate)
                elif it.holiday_type == 'schedule_day':
                    over_time_allowance += (it.morning_hours * employee_rate * overtime_morning_rate)
                    over_time_allowance += (it.night_hours * employee_rate * overtime_night_rate)

        if over_time_allowance:
            payslip_input_type = self.env['hr.payslip.input.type'].search([('code', '=', 'OVERTIME')])
            res.write({'input_line_ids': [(0, 0, {
                # 'name': 'Total overtime',
                # 'sequence': 10,
                # 'code': 'OVERTIME',
                # 'contract_id': res.contract_id.id,
                'amount': over_time_allowance,
                'input_type_id': payslip_input_type.id
            })]})

        for it in filtered_over_time_data:
            it.state = 'done'
            it.payslip_id = res.id

        return res

