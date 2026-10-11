"""Read the public GitHub calendar; reject incomplete responses."""
from datetime import date, timedelta
from html.parser import HTMLParser
import re
from urllib.request import Request, urlopen


class Calendar(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cells, self.counts = {}, {}
        self.target, self.caption = None, ''

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'data-date' in attrs and 'data-level' in attrs:
            self.cells[attrs['id']] = attrs['data-date']
        if tag == 'tool-tip':
            self.target, self.caption = attrs.get('for'), ''

    def handle_data(self, data):
        if self.target:
            self.caption += data

    def handle_endtag(self, tag):
        if tag == 'tool-tip' and self.target:
            match = re.match(r'(No|[\d,]+) contributions? on ', self.caption.strip())
            if match:
                self.counts[self.target] = 0 if match[1] == 'No' else int(match[1].replace(',', ''))
            self.target = None

    def days(self):
        if len(self.cells) < 350 or not self.cells.keys() <= self.counts.keys():
            raise ValueError('Incomplete GitHub contribution calendar; keeping previous assets.')
        return sorted((day, self.counts[key]) for key, day in self.cells.items())


def summarize(days):
    if not days:
        raise ValueError('Empty contribution calendar')
    for previous, current in zip(days, days[1:]):
        if date.fromisoformat(current[0]) - date.fromisoformat(previous[0]) != timedelta(days=1):
            raise ValueError('Contribution calendar has missing or duplicate days')
    longest = running = 0
    for _, count in days:
        running = running + 1 if count > 0 else 0
        longest = max(longest, running)
    # A quiet current day does not end yesterday's streak until today ends.
    tail = days if days[-1][1] else days[:-1]
    current = 0
    for _, count in reversed(tail):
        if not count:
            break
        current += 1
    return {'total': sum(count for _, count in days), 'current': current,
            'longest': longest, 'start': days[0][0], 'end': days[-1][0]}


def fetch_contributions(username):
    request = Request(f'https://github.com/users/{username}/contributions',
                      headers={'User-Agent': 'profile-dashboard', 'Accept-Language': 'en-US'})
    with urlopen(request, timeout=30) as response:
        parser = Calendar()
        parser.feed(response.read().decode('utf-8'))
    return summarize(parser.days())
