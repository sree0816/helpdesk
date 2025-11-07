from django.urls import path
from agents import views
urlpatterns=[path('agenthome/',views.agenthome,name='agenthome'),
             path('login/',views.login,name='login'),
             path('agent_dashboard/',views.agent_dashboard,name='agent_dashboard')]