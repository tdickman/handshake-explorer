from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    re_path('block/(?P<block_hash>[a-f0-9]{64})$', views.block),
    path('block/<int:block_hash>', views.block),
    path('blocks', views.blocks),
    path('names', views.names),
    path('blocks/page/<int:page>', views.blocks),
    path('name/<str:name>', views.name),
    re_path('tx/(?P<tx_hash>[a-f0-9]{64})$', views.transaction),
    re_path('address/(?P<address>[a-z0-9]{42})$', views.address),
]
