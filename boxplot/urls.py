from django.conf.urls import url

from . import views

app_name = 'boxplot'
urlpatterns = [
    url(r'^$', views.get_page, name='box_plot_page'),
    url(r'^result/$', views.algorithm, name='box_plot_result_page'),
    url(r'^result/get-graph/$', views.get_graph, name='box_plot_graph'),
]