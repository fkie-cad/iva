import unittest
from datetime import datetime
from local_repositories.tasks import datetime_utils as time_utils


TIME_A = '14:01:00'
TIME_B = '14:00:00'
TIME = '10:04:07'
DATETIME_STR = '2016-12-21 10:04:07.769764'
DATETIME_STR_TOMORROW = '2016-12-22 10:04:07.769764'
FORMAT = '%Y-%m-%d %H:%M:%S.%f'
DATETIME = datetime.strptime(DATETIME_STR, FORMAT)


class TestDateTimeUtils(unittest.TestCase):

    def test_calculate_time_delta(self):
        seconds = time_utils.calculate_delta_time(TIME_A, TIME_B)
        self.assertEqual(60, seconds)

        seconds = time_utils.calculate_delta_time(TIME_B, TIME_A)
        # one day minus 60 seconds
        self.assertEqual(86340, seconds)

    def test_calculate_time_delta_returns_sixty_seconds_when_times_equal(self):
        self.assertEqual(60, time_utils.calculate_delta_time(TIME_A, TIME_A))

    def test_get_time_from_datetime(self):
        self.assertEqual(TIME, time_utils.get_time_from_datetime(DATETIME))

    def test_verify_time_format_returns_true(self):
        self.assertTrue(time_utils.verify_time_format(TIME_A))
        self.assertTrue(time_utils.verify_time_format(TIME_B))

    def test_verify_time_format_returns_false(self):
        self.assertFalse(time_utils.verify_time_format('0415615'))
        self.assertFalse(time_utils.verify_time_format('00:00'))
        self.assertFalse(time_utils.verify_time_format('ab:cd:ef'))

    def test_add_one_day_to_datetime(self):
        tomorrow = time_utils.add_one_day(DATETIME)
        self.assertEqual(DATETIME_STR_TOMORROW, str(tomorrow))

    def test_update_time_in_datetime(self):
        updated_datetime = time_utils.update_time_in_datetime(DATETIME, TIME_A)
        self.assertEqual(updated_datetime.strftime('%H:%M:%S'), TIME_A)

if __name__ == '__main__':
    unittest.main()
