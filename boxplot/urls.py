from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.get_page, name='box_plot_page'),
    url(r'^result/$', views.get_result_page, name='box_plot_result_page'),
    url(r'^result/get-graph/$', views.get_graph, name='box_plot_graph'),
]