import sys
from datetime import date, timedelta
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from contributions import Calendar, summarize


class StreakTests(unittest.TestCase):
    def summary(self, counts):
        return summarize([((date(2026, 1, 1) + timedelta(days=i)).isoformat(), n)
                          for i, n in enumerate(counts)])

    def test_today_in_progress_preserves_yesterday(self):
        self.assertEqual(self.summary([0, 2, 4, 0])['current'], 2)

    def test_inactive_yesterday_breaks_streak(self):
        self.assertEqual(self.summary([3, 2, 0, 0])['current'], 0)

    def test_counts_days_not_number_of_commits(self):
        result = self.summary([1, 8, 1, 0, 5])
        self.assertEqual((result['total'], result['current'], result['longest']), (15, 1, 3))

    def test_no_activity(self):
        self.assertEqual(self.summary([0, 0, 0])['longest'], 0)

    def test_history_preserves_counts_for_charts(self):
        result = self.summary([2, 0, 7])
        self.assertEqual(sum(day['count'] for day in result['days']), result['total'])
        self.assertEqual(result['days'][-1]['date'], result['end'])

    def test_gaps_rejected(self):
        with self.assertRaises(ValueError):
            summarize([('2026-01-01', 1), ('2026-01-03', 1)])

    def test_calendar_counts_and_incomplete_response(self):
        parser = Calendar()
        parser.feed('<td id="a" data-date="2026-01-01" data-level="4"></td>'
                    '<tool-tip for="a">1,234 contributions on January 1st.</tool-tip>')
        self.assertEqual(parser.counts['a'], 1234)
        with self.assertRaises(ValueError):
            parser.days()
