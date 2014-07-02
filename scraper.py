#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import datetime
import os
import re
import urlparse

import bs4

os.environ['DJANGO_SETTINGS_MODULE'] = 'sayit_philadelphia.settings'

BASE_DIR = os.path.dirname(__file__)
CACHE_DIR = os.path.join(BASE_DIR, 'data')

from speeches.models import Section

from speeches.utils.scraping import BaseParser, prevnext, ScrapingError
from speeches.utils.scraping import ParserSpeech as Speech


class PhilaParser(BaseParser):
    # instance = 'philadelphia'
    instance = 'default'
    # TODO Fix to go off a stable identifier rather than a name
    name_fixes = {
        'Councilwoman Bass': 'Cindy Bass',
        'Councilwoman Blackwell': 'Jannie L. Blackwell',
        'Councilwoman Reynolds Brown': 'Blondell Reynolds Brown',
        'Councilwoman Brown': 'Blondell Reynolds Brown',
        'Council President Clarke': 'Darrell L. Clarke',
        'Councilman Goode': 'W. Wilson Goode, Jr.',
        'Councilman Green': 'Bill Green',
        'Councilman Greenlee': 'William K. Greenlee',
        'Councilman Henon': 'Bobby Henon',
        'Councilman Johnson': 'Kenyatta Johnson',
        'Councilman Jones': 'Curtis Jones, Jr.',
        'Councilman Kenney': 'James F. Kenney',
        'Councilman Oh': 'David Oh',
        "Councilman O'Brien": "Dennis O'Brien",
        "Councilman O'Neill": "Brian J. O'Neill",
        'Councilwoman Sanchez': 'Maria D. Quiñones-Sánchez',
        'Councilman Squilla': 'Mark Squilla',
        'Councilwoman Tasco': 'Marian Tasco',
    }

    def _add_parser_options(self):
        super(PhilaParser, self)._add_parser_options()

        self.parser.add_option(
            '--year',
            dest='year',
            help='Year to search for',
            action='store',
            type='int',
            )
        self.parser.add_option(
            '--current-year',
            dest='current_year',
            help='Search for the current calendar year.',
            action='store_true',
            )
        self.parser.add_option(
            '--last-year',
            dest='last_year',
            help='Search for the previous calender year.',
            action='store_true',
            )
        self.parser.add_option(
            '--month',
            dest='month',
            help='Month to search for',
            action='store',
            type='string',
            )
        self.parser.add_option(
            '--day',
            dest='day',
            help='Day of month to search for',
            action='store',
            type='int',
            )
        self.parser.add_option(
            '--index-url',
            dest='index_url',
            help="URL of the search page for this type of transcript.",
            action='store',
            type='string',
            )
        self.parser.add_option(
            '--committee-name',
            dest='committee_name',
            help='Name of the committee to fetch',
            action='store',
            type='string',
            )

    def _process_parser_options(self):
        super(PhilaParser, self)._process_parser_options()

        if self.options.current_year:
            self.year = datetime.datetime.now().year
        elif self.options.last_year:
            self.year = datetime.datetime.now().year - 1
        else:
            self.year = self.options.year

        self.month = self.options.month
        self.day = self.options.day

        self.index_url = self.options.index_url
        self.committee_name = self.options.committee_name

        month = self.options.month
        if month:
            self.month = month
            day = self.options.day
            self.day = '{0:02d}'.format(day) if day else 'All Days'
        else:
            self.month = 'ALL MONTHS'
            self.day = None

    def get_transcripts(self):
        get_resp = self.requests.get(self.index_url)

        soup = bs4.BeautifulSoup(get_resp.content)
        form = soup.find('form', id='Form1')

        # FIXME - don't cache the index page.
        post_data = {
            '__VIEWSTATE': form.find('input', id='__VIEWSTATE')['value'],
            '__EVENTVALIDATION': form.find(
                'input', id='__EVENTVALIDATION')['value'],
            'Button3': 'submit',
            'ddlYear': self.year,
            'ddlMonth': self.month,
            }

        if self.committee_name:
            post_data['ddlCommittee'] = self.committee_name

        if self.day:
            post_data['ddlDay'] = self.day

        resp = self.requests.post(self.index_url, data=post_data)

        soup = bs4.BeautifulSoup(resp.content)

        # I'm not really happy with this, but it seems like the least bad
        # option available for finding all these documents. Let's hope the
        # text doesn't change!
        trs = [x.find_parent('tr')
               for x in soup.findAll(text='Retrieve Document')]

        for tr in trs:
            tds = tr.findAll('td')

            committee_name = tds[0].font.text.strip()

            date = datetime.datetime.strptime(
                tds[1].font.text.strip(), '%m/%d/%Y').date()
            url = urlparse.urljoin(self.index_url, tds[2].a['href'])
            try:
                text = self.get_pdf(url)
            except ScrapingError:
                print "SKIPPING {} - error downloading".format(url)
            else:
                if text:
                    yield {
                        'date': date,
                        'url': url,
                        'text': text,
                        'committee_name': committee_name,
                        }

    def top_section_title(self, data):
        return '{date}'.format(
            committee_name=data['committee_name'],
            date=data['date'].strftime('%d %B %Y').lstrip('0'),
            )

    def get_parent_section(self, data):
        return self.get_or_create(
            Section,
            instance=self.instance,
            title=data['committee_name'],
            )

    def parse_transcript(self, data):
        print "PARSING %s" % data['url']

        page, num = 1, 1

        speech = None
        state = 'text'
        Speech.reset(True)

        for prev_line, line, next_line in prevnext(data['text']):
            # Page break
            if '\014' in line:
                page += 1
                num = 0
                continue

            if state == 'skip1':
                state = 'text'
                continue

            # Empty line, or line matching page footer
            if re.match('\s*$', line):
                continue
            if re.match(' *Strehlow & Associates, Inc.$| *\(215\) 504-4622$',
                        line):
                continue

            # Ignore title page for now
            if page == 1:
                continue

            # Start of certificate/index
            if re.match(
                    ' *\d+ *(CERTIFICATE|C E R T I F I C A T I O N)$',
                    line):
                state = 'index'
            if state == 'index':
                continue

            # Each page starts with page number
            if num == 0:
                m = re.match(' +(\d+)$', line)
                assert int(m.group(1)) == page
                num += 1
                continue

            # Heading somewhere within this page, just ignore it
            if num == 1:
                num += 1
                continue

            # Let's check we haven't lost a line anywhere...
            assert re.match(' *%d(   |$)' % num, line), \
                '%s != %s' % (num, line)
            line = re.sub('^ *%d(   |$)' % num, '', line)
            num += 1

            # Ignore line containing only a number and then dashes
            if re.match('[\s-]*$', line):
                continue

            # Narrative messages
            m = re.match(' +(\(.*\))$', line)
            if m:
                yield speech
                speech = Speech(speaker=None, text=line)
                continue
            m1 = re.match(' +(\(.*)$', line)
            m2 = re.match(' *\d+ +(.*\))$', next_line)
            if m1 and m2:
                yield speech
                speech = Speech(
                    speaker=None,
                    text='%s %s' % (m1.group(1), m2.group(1)),
                    )
                state = 'skip1'
                num += 1
                continue

            # Okay, here we have a non-empty, non-page number, non-narrative
            # line of just text print page, num, line

            # New speaker
            m = re.match(" *([A-Z '.]+):(?: (.*)|$)", line)
            if m:
                yield speech
                speaker = self.fix_name(m.group(1))
                text = m.group(2) or ''
                speech = Speech(speaker=speaker, text=text)
                continue

            # We must now already have a speech by the time we're here
            if not speech:
                raise Exception(
                    'Reached here without a speech - need to deal with "%s"' %
                    line)

            if re.match(' ', line):
                speech.add_para(line.strip())
            else:
                speech.add_text(line.strip())

        yield speech


parser = PhilaParser(cache_dir=CACHE_DIR)
parser.run()
