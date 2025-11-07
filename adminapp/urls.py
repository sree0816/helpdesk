from django.urls import path
from adminapp import views
urlpatterns=[path('adminhome/',views.adminhome,name='adminhome'),
             path('dashboard/',views.dashboard,name='dashboard'),
             path('register/',views.register,name='register'),
             path('save_agent/',views.save_agent,name='save_agent')]