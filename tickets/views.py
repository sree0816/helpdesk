from django.shortcuts import render,redirect
from .models import Ticket
from agents.models import Agent
from django.core.mail import send_mail
from django.conf import settings

# Create your views here.
def tickethome(request):
    return render(request,'tickethome.html')

def create(request):
    return render(request,'createticket.html')
def create_ticket(request):
    if request.method == 'POST':
        title = request.POST['title']
        desc = request.POST['description']
        email = request.POST['email']
        priority = request.POST['priority']

        ticket = Ticket.objects.create(
            title=title,
            description=desc,
            email=email,
            priority=priority,
            sla_hours=24
        )

        # auto assign agent if available
        available_agent = Agent.objects.filter(is_available=True).first()
        if available_agent:
            ticket.assigned_agent = available_agent
            ticket.status = 'in_progress'
            ticket.save()

            available_agent.is_available = False
            available_agent.save()

            send_mail(
                'Ticket Assigned',
                f'Your ticket "{title}" has been assigned to {available_agent.name}.',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=True
            )
        else:
            print("No agents available currently")

    return redirect('createsuccess')

    return render(request, 'create_ticket.html')
def createsuccess(request):
    return render(request,'createsuccess.html')

