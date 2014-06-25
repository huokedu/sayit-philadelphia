from datetime import date

from django.db.models import Q

from popolo.views import OrganizationDetailView

from speeches.models import Section, Speaker
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

class CommitteeDetailView(OrganizationDetailView):
    template_name = 'committee_detail.html'

    def get_object(self, *args, **kwargs):
        queryset = self.get_queryset()
        # Should probably have proper slug extension of Organization
        # Or at least needs to handle Legislative Oversight Committee,
        # "the", "&"
        slug = self.kwargs['slug']
        slug = 'Committee on %s' % self.kwargs['slug']
        obj = queryset.filter(name__iexact=slug).get()
        return obj

    def get_context_data(self, *args, **kwargs):
        context = super(CommitteeDetailView, self).get_context_data(
            *args, **kwargs)

        context['members'] = Speaker.objects.filter(
            memberships__organization=self.object)

        try:
            context['section'] = Section.objects.get(
                title__iexact=self.object.name)
        except:
            pass

        return context
