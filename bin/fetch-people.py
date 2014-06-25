#!/usr/bin/env python

import json
import os
import re
import unicodedata

import bs4
import requests
import requests_cache

os.environ['DJANGO_SETTINGS_MODULE'] = 'sayit_philadelphia.settings'

BASE_DIR = os.path.dirname(__file__)
CACHE_DIR = os.path.join(BASE_DIR, 'data')
requests_cache.install_cache(CACHE_DIR)

def slugify(value):
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    return re.sub('[-\s]+', '-', value)

people = {}
organizations = {}
memberships = []

def get_person(link):
    url = link['href']
    name = ' '.join(link(text=True)).strip().replace(u'\u2019', "'")
    if url not in people:
        m = re.search('(?: |-)([^ -]+?)(?:, Jr\.)?$', name)
        family_name = m.group(1)
        if family_name == 'Brown': family_name = 'Reynolds Brown'
        people[url] = {
            'id': slugify(name),
            'name': name,
            'family_name': family_name,
            'links': [
                { 'url': url, 'note': 'Official site' }
            ]
        }
    return people[url]['id']

def get_org(link):
    name = link.string
    if name not in organizations:
        organizations[name] = {
            'id': slugify(name),
            'name': name,
            'classification': 'Committee',
            'links': [
                { 'url': link['href'], 'note': 'Official site' }
            ]
        }
    return organizations[name]

def add_membership(role, org, link):
    memberships.append({
        'label': role + ' of ' + org['name'],
        'role': role,
        'person_id': get_person(link),
        'organization_id': org['id'],
    })

soup = bs4.BeautifulSoup(requests.get('http://philadelphiacitycouncil.net/standing-committees/').text)
committees = soup.find(id='menu-standing-committees').find_all('a')
for link in committees:
    soup = bs4.BeautifulSoup(requests.get(link['href']).text)
    comm = get_org(link)

    content = soup.find(class_='post-entry')
    for el in content.contents:
        if isinstance(el, bs4.NavigableString):
            # Ignore whitespace
            if not re.match('^\s*$', el):
                raise Exception, el
        elif el.name == 'h3':
            hdg = el.string
        elif el.name == 'p' and hdg == 'Responsiblity':
            summary = ' '.join(el(text=True))
            summary = comm.get('summary', '') + '\n\n' + summary
            comm['summary'] = summary.strip()
        elif el.name == 'p' and hdg in ('Chair', 'Vice Chair'):
            links = el('a')
            assert len(links) == (2 if 'Public Health' in comm['name'] and hdg == 'Vice Chair' else 1), (hdg, el)
            for link in links:
                add_membership(hdg, comm, link)
        elif el.name == 'p':
            if hdg == 'Hearing Materials': continue
            assert hdg == 'Members', hdg
            if el.string and not el.a:
                assert re.search('(?i)Consisting of (all|not less than five \(5\)) members', el.string), el.string
            else:
                links = el('a')
                links = [ l for l in links if l.string != '.' ]
                if el.string:
                    assert len(links) == 1
                else:
                    assert len(links) >= 4, (hdg, len(links))
                for link in links:
                    add_membership('Member', comm, link)
        else:
            raise Exception, el

# Councillors overall
organizations['Council'] = {
    'id': 'city-council',
    'classification': 'Council',
    'name': 'Philadelphia City Council',
    'links': [ { 'url': 'http://philadelphiacitycouncil.net/', 'note': 'Official site' } ],
}
for person in people.values():
    data = {
        'label': 'Philadelphia City Councillor',
        'role': 'Councillor',
        'person_id': person['id'],
        'organization_id': 'city-council',
    }
    if person['id'] == 'bill-green':
        data['start_date'] = '2008-01-07'
        data['end_date'] = '2014-02'
    memberships.append(data)

out = {
    'persons': people.values(),
    'organizations': organizations.values(),
    'memberships': memberships,
}
print json.dumps(out, separators=(',', ': '), indent=2, sort_keys=True)
