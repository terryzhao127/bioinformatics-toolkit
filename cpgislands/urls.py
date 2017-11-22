from django.conf.urls import url

from . import views

app_name = 'cpgislands'
urlpatterns = [
    url(r'^$', views.get_page, name='cpgislands_page'),
    url(r'^result/$', views.algorithm, name='cpgislands'),
]