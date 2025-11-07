from django.urls import path
from tickets import views
urlpatterns=[path('tickethome/',views.tickethome,name='tickethome'),
             path('create/',views.create,name='create'),
             path('createsuccess/',views.createsuccess,name='createsuccess'),
             path('create_ticket/',views.create_ticket,name='create_ticket')
             ]