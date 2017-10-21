from django.conf.urls import url

from . import views

app_name = 'fasta'
urlpatterns = [
    url(r'^$', views.get_page, name='fasta_page'),
    url(r'^result/$', views.algorithm, name='fasta'),
]