from django.conf.urls import url
from . import views

app_name = 'smithwaterman'
urlpatterns = [
    url(r'^$', views.get_page, name='smith_waterman_page'),
    url(r'^result/$', views.algorithm, name='smith_waterman_algorithm'),
]