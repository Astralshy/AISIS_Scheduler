from django.conf.urls import url

from .views import CustomSectionView, ScraperView, ScheduleClasses, SchedulePKView, ScheduleView


urlpatterns = [
    url('seclist/(?P<pk>[0-9]+)/$',CustomSectionView.as_view()),
    url('scraper/', ScraperView.as_view()),
    url('sched/(?P<pk>[0-9]+)/$', SchedulePKView.as_view()),
    url('sched/$', ScheduleView.as_view()),
    url('schedclass/',ScheduleClasses.as_view())
]