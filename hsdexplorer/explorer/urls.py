from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    re_path('block/(?P<block_hash>[a-f0-9]{64})$', views.block, name='block'),
    path('block/<int:block_hash>', views.block),
    path('search', views.search),
    path('names', views.names),
    re_path('names/page/(?P<page>\d+)$', views.names),
    path('blocks', views.blocks),
    path('blocks/page/<int:page>', views.blocks),
    path('events', views.events),
    path('events/page/<int:page>', views.events),
    path('name/<str:name>', views.name, name='name'),
    re_path('tx/(?P<tx_hash>[a-f0-9]{64})$', views.transaction, name='transaction'),
    re_path('address/(?P<address>[a-z0-9]{42})$', views.address, name='address'),
    re_path('address/(?P<address>[a-z0-9]{42})/page/(?P<page>\d+)$', views.address),
]
