import logging
import pprint
import datetime
import math
from odoo.tools.float_utils import float_round


from odoo import models, fields, api

LOGGER = logging.getLogger(__name__)


def float_to_time(float_hour):
    if float_hour == 24.0:
        return datetime.time.max
    return datetime.time(int(math.modf(float_hour)[1]), int(float_round(60 * math.modf(float_hour)[0], precision_digits=0)), 0)



class ResourceCalendar(models.Model):
    """Resource Inherited Model"""
    _inherit = 'resource.calendar'



    ##omara added 14 han2021, from odoo11 base
    def _get_weekdays(self):
        """ Return the list of weekdays that contain at least one working
        interval. """
        self.ensure_one()
        return list({int(d) for d in self.attendance_ids.mapped('dayofweek')})
    ##
    @staticmethod
    def _extract_interval(leave):
        """
        Extract interval from leave object along with any other needed data
        :param <hr.holidays> leave:
        :return: tuple of leave interval
        :rtype: (<datetime.datetime> date_from, <datetime.datetime> date_to)
        """
        _date_from = fields.Datetime.from_string(leave.date_from)
        _date_to = fields.Datetime.from_string(leave.date_to)
        return _date_from, _date_to

    # TODO: I think this method should be in resource.calendar.leave model
    @api.model
    def get_leave_intervals(self, resource_id, date_from, date_to, include_leave_types=None, exclude_leave_types=None):
        """
        Return leave intervals for selected resource (employee).
        Get all intervals that intersect with interval starting at :param: date_from
        and ending at :param: date_to.

        Note: there could be a value in either include_leave_types or exclude_leave_types, if include_leave_types
        has value, then exclude_leave_types is ignored. If both are none, then all leave types are considered.

        :param [<hr.holidays.status>, ] include_leave_types: leave types to only include, so that don't only fetch
                                                             leaves of such types in the given interval from
                                                             :param date_from: to :param date_to:

        :param [<hr.holidays.status>, ] exclude_leave_types: leave types to exclude, so that don't fetch
                                                             leaves of such types in the given interval from
                                                             :param date_from: to :param date_to:
        :return: list of leave intervals
        """
        calendar_leaves_model = self.env['resource.calendar.leaves']
        domain = [('resource_id', '=', resource_id),
                  '|',
                  '&', ('date_from', '<', date_from),
                  ('date_to', '>', date_to),
                  '|',
                  '&', ('date_from', '>=', date_from),
                  ('date_from', '<=', date_to),
                  '&', ('date_to', '>=', date_from),
                  ('date_to', '<=', date_to),
                  ]

        if include_leave_types:
            LOGGER.debug('Leaves Included: %s', include_leave_types)
            include_leave_type_ids = [_leave.id for _leave in include_leave_types]
            domain.insert(0, ('leave_type', 'in', include_leave_type_ids))
        elif exclude_leave_types:
            LOGGER.debug('Leaves Excluded: %s', exclude_leave_types)
            exclude_leave_type_ids = [_leave.id for _leave in exclude_leave_types]
            domain.insert(0, ('leave_type', 'not in', exclude_leave_type_ids))

        approved_leaves = calendar_leaves_model.search(domain)

        return map(self._extract_interval, approved_leaves)

    # TODO: I think this method should be in resource.calendar.leave model
    @api.model
    def get_leave_intervals_including_public_vacations(self, resource_id, date_from, date_to, include_leave_types=None,
                                                       exclude_leave_types=None):
        """
        Includes public vacations, as intervals, to normal leaves.

        Note: there could be a value in either include_leave_types or exclude_leave_types, if include_leave_types
        has value, then exclude_leave_types is ignored. If both are none, then all leave types are considered.

        :param resource.resource resource_id:
        :param str date_from:
        :param str date_to:
        :param [<hr.holidays.status>, ] include_leave_types: leave types to only include, so that don't  only fetch
                                                             leaves of such types in the given interval from
                                                             :param date_from: to :param date_to:

        :param [<hr.holidays.status>, ] exclude_leave_types: leave types to exclude, so that don't fetch
                                                             leaves of such types in the given interval from
                                                             :param date_from: to :param date_to:
        :rtype: [(<datetime.datetime> date_from, <datetime.datetime> date_to), ]
        """
        public_holidays_model = self.env['hr.holidays.public']
        public_holidays = public_holidays_model.get_public_holidays(date_from, date_to)
        leaves = self.get_leave_intervals(resource_id, date_from, date_to)

        LOGGER.debug('Normal holiday intervals from %s to %s: \n%s', date_from, date_to,
                     pprint.pformat(leaves))
        return list(leaves) + public_holidays

    def _iter_day_attendance_intervals(self, day_date, start_time, end_time):
        """ Get an iterator of all interval of current day attendances. """
        for calendar_working_day in self._get_day_attendances(day_date, start_time, end_time):
            if self.type == 'flexible':
                from_time = float_to_time(calendar_working_day.hour_from_start)
                to_time = float_to_time(calendar_working_day.hour_to_start)
            else:
                from_time = float_to_time(calendar_working_day.hour_from)
                to_time = float_to_time(calendar_working_day.hour_to)

            dt_f = datetime.datetime.combine(day_date, max(from_time, start_time))
            dt_t = datetime.datetime.combine(day_date, min(to_time, end_time))

            yield self._interval_new(dt_f, dt_t, {'attendances': calendar_working_day})

