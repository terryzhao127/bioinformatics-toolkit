from django.conf.urls import url
from . import views

app_name = 'phylogenetictree'
urlpatterns = [
    url(r'^$', views.get_page, name='phylogenetic_tree_page'),
    url(r'^result/$', views.result_page, name='phylogenetic_tree_result'),
    url(r'^result/get-tree/$', views.get_tree, name='phylogenetic_tree'),
]