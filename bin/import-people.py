#!/usr/bin/env python

import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'sayit_philadelphia.settings'

from speeches.models import Speaker
from popolo.models import Organization, Membership
from instances.models import Instance

data = json.load(open(sys.argv[1]))
instance = Instance.objects.get(label='default')

for o in data['organizations']:
    org, created = Organization.objects.get_or_create(
        identifiers__identifier=o['id'],
        defaults={
            'name': o['name'],
            'classification': o['classification'],
        }
    )
    if created:
        org.identifiers.create(
            identifier=o['id'],
            scheme='JSON',
        )
        org.links.create(
            url=o['links'][0]['url'],
            note=o['links'][0]['note'],
        )

for person in data['persons']:
    spkr, created = Speaker.objects.get_or_create(
        instance=instance,
        identifiers__identifier=person['id'],
        defaults={
            'name': person['name'],
            'family_name': person['family_name']
        }
    )
    if created:
        spkr.identifiers.create(
            identifier=person['id'],
            scheme='JSON',
        )
        spkr.links.create(
            url=person['links'][0]['url'],
            note=person['links'][0]['note'],
        )

for mship in data['memberships']:
    person = Speaker.objects.get(identifiers__identifier=mship['person_id'])
    org = Organization.objects.get(identifiers__identifier=mship['organization_id'])
    data = {
        'label': mship['label'],
        'role': mship['role'],
        'person': person,
        'organization': org,
    }
    if 'start_date' in mship:
        data['start_date'] = mship['start_date']
    if 'end_date' in mship:
        data['end_date'] = mship['end_date']
    Membership.objects.get_or_create(**data)
