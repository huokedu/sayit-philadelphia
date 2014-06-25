from datetime import date

from django.db.models import Q

from speeches.views import SpeakerList

class CouncilSpeakerList(SpeakerList):
    def get_context_data(self, **kwargs):
        context = super(CouncilSpeakerList, self).get_context_data(**kwargs)

        today = date.today().isoformat()

        cllrs = Q(memberships__role='Councillor')
        ended_after_today = Q(memberships__end_date__gte=today) | Q(memberships__end_date__isnull=True)
        ended_before_today = Q(memberships__end_date__lt=today)
        started_before_today = Q(memberships__start_date__lte=today) | Q(memberships__start_date__isnull=True)

        current = cllrs & ended_after_today & started_before_today
        previous = cllrs & ended_before_today

        context['speaker_list_councillor_current'] = context['speaker_list'].filter(current)
        context['speaker_list_councillor_previous'] = context['speaker_list'].filter(previous)
        context['speaker_list_other'] = context['speaker_list'].exclude(cllrs)
        return context
