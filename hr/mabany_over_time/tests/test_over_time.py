from odoo.tests import TransactionCase
from datetime import datetime
from odoo.tests import tagged

INPUT_DATA = [
    {   # TEST: 1
        'date_from': '2020-01-07 05:00:00',
        'date_to': '2020-01-07 07:00:00',
        'morning_start_hour': '05',
        'expected_morning_hours': 2.0,
        'expected_night_hours': 0.0,
    },
    {   # TEST: 2
        'date_from': '2020-01-07 11:00:00',
        'date_to': '2020-01-07 12:00:00',
        'morning_start_hour': '05',
        'expected_morning_hours': 1.0,
        'expected_night_hours': 0.0,
    },
    {   # TEST: 3
        'date_from': '2020-01-07 13:00:00',
        'date_to': '2020-01-07 15:00:00',
        'morning_start_hour': '05',
        'expected_morning_hours': 2.0,
        'expected_night_hours': 0.0,
    },
    {   # TEST: 4
        'date_from': '2020-01-07 17:00:00',
        'date_to': '2020-01-07 18:00:00',
        'morning_start_hour': '05',
        'expected_morning_hours': 0.0,
        'expected_night_hours': 1.0,
    },
    {    # TEST: 5
        'date_from': '2020-01-07 16:00:00',
        'date_to': '2020-01-07 18:00:00',
        'morning_start_hour': '05',
        'expected_morning_hours': 1.0,
        'expected_night_hours': 1.0,
    },
    {   # TEST: 6
        'date_from': '2020-01-07 17:00:00',
        'date_to': '2020-01-07 18:00:00',
        'morning_start_hour': '05',
        'expected_morning_hours': 0.0,
        'expected_night_hours': 1.0,
    },
    {   # TEST: 7
        'date_from': '2020-01-07 18:00:00',
        'date_to': '2020-01-08 00:00:00',
        'morning_start_hour': '05',
        'expected_morning_hours': 0.0,
        'expected_night_hours': 6.0,
    },
    {   # TEST: 8
        'date_from': '2020-01-07 18:00:00',
        'date_to': '2020-01-08 03:00:00',
        'morning_start_hour': '05',
        'expected_morning_hours': 0.0,
        'expected_night_hours': 9.0,
    },
    {   # TEST: 9
        'date_from': '2020-01-07 03:00:00',
        'date_to': '2020-01-07 06:00:00',
        'morning_start_hour': '05',
        'expected_morning_hours': 1.0,
        'expected_night_hours': 2.0,
    },
    {   # TEST: 10
        'date_from': '2020-01-07 03:00:00',
        'date_to': '2020-01-07 06:00:00',
        'morning_start_hour': '05',
        'expected_morning_hours': 1.0,
        'expected_night_hours': 2.0,
    },
    {   # TEST: 11
        'date_from': '2020-01-07 03:00:00',
        'date_to': '2020-01-07 06:30:00',
        'morning_start_hour': '05',
        'expected_morning_hours': 1.5,
        'expected_night_hours': 2.0,
    },
    {   # TEST: 12
        'date_from': '2020-01-07 03:00:00',
        'date_to': '2020-01-07 06:30:00',
        'morning_start_hour': '09',
        'expected_morning_hours': 0.0,
        'expected_night_hours': 3.5,
    },
    {   # TEST: 13
        'date_from': '2020-01-07 12:00:00',
        'date_to': '2020-01-07 18:30:00',
        'morning_start_hour': '05',
        'expected_morning_hours': 5.0,
        'expected_night_hours': 1.5,
    },
    {   # TEST: 14
        'date_from': '2020-01-07 23:00:00',
        'date_to': '2020-01-08 02:00:00',
        'morning_start_hour': '05',
        'expected_morning_hours': 0.0,
        'expected_night_hours': 3.0,
    },
    {   # TEST: 15
        'date_from': '2020-01-07 23:00:00',
        'date_to': '2020-01-08 06:00:00',
        'morning_start_hour': '05',
        'expected_morning_hours': 1.0,
        'expected_night_hours': 6.0,
    },
    {   # TEST: 16
        'date_from': '2020-01-07 15:00:00',
        'date_to': '2020-01-07 21:00:00',
        'morning_start_hour': '05',
        'expected_morning_hours': 2.0,
        'expected_night_hours': 4.0,
    },
]


@tagged('post_install', '-at_install')
class OverTimeTest(TransactionCase):
    def setUp(self):
        super(OverTimeTest, self).setUp()

        self.over_time = self.env['over.time']

    def test_morning_night_hours(self):
        print("==============> BEGIN TEST <=================")
        for idx, it in enumerate(INPUT_DATA):
            date_from = datetime.strptime(it['date_from'], '%Y-%m-%d %H:%M:%S')
            date_to = datetime.strptime(it['date_to'], '%Y-%m-%d %H:%M:%S')
            morning_start_hour = it['morning_start_hour']

            ans = self.over_time._get_morning_night_hours(date_from, date_to, morning_start_hour)

            with self.subTest("Test %s" % str(idx + 1)):
                assert round(ans['morning_hours'], 2) == it['expected_morning_hours']
                assert round(ans['night_hours'], 2) == it['expected_night_hours']
                print("=======> Sub Test %s/%s PASSED" % (str(idx + 1), str(len(INPUT_DATA))))


