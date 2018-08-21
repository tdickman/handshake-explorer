from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    re_path('block/(?P<block_hash>[a-f0-9]{64})$', views.block, name='block'),
    path('block/<int:block_hash>', views.block),
    path('blocks', views.blocks),
    path('search', views.search),
    path('names', views.names),
    path('blocks/page/<int:page>', views.blocks),
    path('name/<str:name>', views.name, name='name'),
    re_path('tx/(?P<tx_hash>[a-f0-9]{64})$', views.transaction, name='transaction'),
    re_path('address/(?P<address>[a-z0-9]{42})$', views.address, name='address'),
    re_path('address/(?P<address>[a-z0-9]{42})/page/(?P<page>\d+)$', views.address),
]
