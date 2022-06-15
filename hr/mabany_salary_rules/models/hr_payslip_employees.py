

from odoo import api, fields, models, _
from collections import defaultdict
import pytz
from datetime import datetime, date, time

class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    def _check_undefined_slots(self, work_entries, payslip_run):
        """
        Check if a time slot in the contract's calendar is not covered by a work entry
        """
        work_entries_by_contract = defaultdict(lambda: self.env['hr.work.entry'])
        for work_entry in work_entries:
            work_entries_by_contract[work_entry.contract_id] |= work_entry

        for contract, work_entries in work_entries_by_contract.items():
            calendar_start = pytz.utc.localize(
                datetime.combine(max(contract.date_start, payslip_run.date_start), time.min))
            calendar_end = pytz.utc.localize(
                datetime.combine(min(contract.date_end or date.max, payslip_run.date_end), time.max))
            outside = contract.resource_calendar_id._attendance_intervals_batch(calendar_start, calendar_end)[
                          False] - work_entries._to_intervals()
            # if outside:
            #     time_intervals_str = "\n - ".join(['', *["%s -> %s" % (s[0], s[1]) for s in outside._items]])
            #     # raise UserError(
            #     #     _("Some part of %s's calendar is not covered by any work entry. Please complete the schedule. Time intervals to look for:%s") % (
            #     #     contract.employee_id.name, time_intervals_str))
