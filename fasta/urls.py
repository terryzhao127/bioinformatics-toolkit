from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.get_page, name='fasta_page'),
    url(r'^result/$', views.fasta, name='fasta'),
]