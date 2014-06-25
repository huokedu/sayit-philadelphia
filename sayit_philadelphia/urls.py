from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from sayit_philadelphia.views import CouncilSpeakerList, CommitteeDetailView

# Admin section
from django.contrib import admin
admin.autodiscover()

urlpatterns = staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += patterns('',
    url(r'^speakers$', CouncilSpeakerList.as_view(), name='speaker-list'),
    url(r'^committee/(?P<slug>.+)$',
        CommitteeDetailView.as_view(),
        name='committee_detail'),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'', include('speeches.urls', app_name='speeches', namespace='speeches')),
)
