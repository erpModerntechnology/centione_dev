from odoo import models, fields, api
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def _get_date_from_default(self):
        date_start = date.today().replace(month=date.today().month-1)
        defualt_date_from = date_start + timedelta(days=17)
        return defualt_date_from

    def _get_date_to_default(self):
        date_end = self._get_date_from_default() + relativedelta(months=1, days=-1)
        return date_end


    date_from = fields.Date(
        string='From', readonly=True, required=True,
        default=_get_date_from_default,
        states={'draft': [('readonly', False)], 'verify': [('readonly', False)]})
    date_to = fields.Date(
        string='To', readonly=True, required=True,
        default=_get_date_to_default,
        states={'draft': [('readonly', False)], 'verify': [('readonly', False)]})





    # @api.onchange('employee_id')
    # def get_terminated_contract(self):
    #     terminated = []
    #     contract = self.env['hr.contract'].search([('employee_id','=',self.employee_id.id),('state','=','cancel')])
    #     if contract:
    #         terminated.append(contract.id)
    #         convert_to_str = [str(rec.id) for rec in contract]
    #         fully = "".join(convert_to_str)
    #         self.contract_id = int(fully)
    #
    #     lost = self.env['hr.payslip'].search([('id', '!=', self._origin.id)])
    #     if lost:
    #         for rec in lost:
    #             if contract:
    #                 if rec.employee_id == contract.employee_id:
    #                         self.contract_id = None

