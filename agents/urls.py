from django.urls import path
from agents import views
urlpatterns=[path('agenthome/',views.agenthome,name='agenthome'),
             path('login/',views.login,name='login'),
             path('agent_dashboard/',views.agent_dashboard,name='agent_dashboard'),
             path('update_ticket/<int:ticket_id>/', views.update_ticket, name='update_ticket'),
path('logout/', views.logout_agent, name='logout_agent')
             ]