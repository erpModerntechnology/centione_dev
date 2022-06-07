import logging

from odoo import models, fields, api

LOGGER = logging.getLogger(__name__)


class Contract(models.Model):
    _inherit = 'hr.contract'

    # @api.one
    def _work_hour_value(self):
        """
            calculate total working hours
        """
        if self.month_workdays == 0 or self.workday_hours == 0:
            self.work_hour_value = 0
        else:
            self.work_hour_value = round((self.wage) / self.month_workdays / self.workday_hours, 2)

    month_workdays = fields.Integer(default=22,
                                    string='Month Workdays',
                                    help="Net month workdays excluding occasional holidays, "
                                         "it's computed as follows: 30 - (4 * weekly_holidays).\n"
                                         "weekly_holidays are calculated from Working Days field")
    workday_hours = fields.Integer('Workday Hours', default=8,
                                   help='It helps compute work hour value based '
                                        'on Wage and Month Workdays')
    work_hour_value = fields.Float(compute=_work_hour_value,
                                   string='Work Hour Value', readonly=True)
