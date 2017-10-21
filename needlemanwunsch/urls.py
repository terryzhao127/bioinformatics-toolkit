from django.conf.urls import url
from . import views

app_name = 'needlemanwunsch'
urlpatterns = [
    url(r'^$', views.get_page, name='needleman_wunsch_page'),
    url(r'^result/$', views.algorithm, name='needleman_wunsch_algorithm'),
]