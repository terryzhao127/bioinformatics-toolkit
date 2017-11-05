from django.conf.urls import url
from . import views

app_name = 'sensingmatrix'
urlpatterns = [
    url(r'^$', views.get_page, name='sensing_matrix_page'),
    url(r'^result/$', views.algorithm, name='sensing_matrix_algorithm'),
]