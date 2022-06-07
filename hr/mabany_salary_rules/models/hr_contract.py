from collections import defaultdict
from datetime import datetime, date
from odoo import fields, models, _
from odoo.exceptions import UserError


class HrContract(models.Model):
    _inherit = 'hr.contract'

    def _generate_work_entries(self, date_start, date_stop, force=False):
        print('aaaaaaaaaaaaaaaaaa')
        canceled_contracts = self.filtered(lambda c: c.state == 'cancel')
        if canceled_contracts:
            # raise UserError(
            #     _("Sorry, generating work entries from cancelled contracts is not allowed.") + '\n%s' % (
            #         ', '.join(canceled_contracts.mapped('name'))))
            vals_list = []
            date_start = fields.Datetime.to_datetime(date_start)
            date_stop = datetime.combine(fields.Datetime.to_datetime(date_stop), datetime.max.time())

            intervals_to_generate = defaultdict(lambda: self.env['hr.contract'])
            for contract in self:
                contract_start = fields.Datetime.to_datetime(contract.date_start)
                contract_stop = datetime.combine(fields.Datetime.to_datetime(contract.date_end or datetime.max.date()),
                                                 datetime.max.time())
                date_start_work_entries = max(date_start, contract_start)
                date_stop_work_entries = min(date_stop, contract_stop)
                if force:
                    intervals_to_generate[(date_start_work_entries, date_stop_work_entries)] |= contract
                    continue

                # In case the date_generated_from == date_generated_to, move it to the date_start to
                # avoid trying to generate several months/years of history for old contracts for which
                # we've never generated the work entries.
                if contract.date_generated_from == contract.date_generated_to:
                    contract.write({
                        'date_generated_from': date_start,
                        'date_generated_to': date_start,
                    })
                # For each contract, we found each interval we must generate
                last_generated_from = min(contract.date_generated_from, contract_stop)
                if last_generated_from > date_start_work_entries:
                    contract.date_generated_from = date_start_work_entries
                    intervals_to_generate[(date_start_work_entries, last_generated_from)] |= contract

                last_generated_to = max(contract.date_generated_to, contract_start)
                if last_generated_to < date_stop_work_entries:
                    contract.date_generated_to = date_stop_work_entries
                    intervals_to_generate[(last_generated_to, date_stop_work_entries)] |= contract

            for interval, contracts in intervals_to_generate.items():
                date_from, date_to = interval
                vals_list.extend(contracts._get_work_entries_values(date_from, date_to))

            if not vals_list:
                return self.env['hr.work.entry']

            return self.env['hr.work.entry'].create(vals_list)
