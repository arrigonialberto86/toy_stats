from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^trial$', views.trial, name='trial'),
    url(r'^trends$', views.trends, name='trends'),
    url(r'^query$', views.query, name='query'),
    url(r'^jobs$', views.jobs, name='jobs'),
    url(r'^jobs_search$', views.jobs_search, name='jobs_search'),
    url(r'^jobs_wordcloud$', views.jobs_wordcloud, name='jobs_wordcloud'),
]
