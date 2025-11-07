from django.shortcuts import render, redirect
from django.contrib import messages
from agents.models import Agent
from tickets.models import Ticket



def agenthome(request):
    return render(request,'agenthome.html')
def login(request):
    return render(request,'login.html')
# def agent_dashboard(request):
#     agent_id=request.session.get('agent_id')
#     if not agent_id:
#         return redirect('login')
#     agent=Agent.objects.get(id=agent_id)
#     tickets=Ticket.objects.filter(assigned_agent=agent)
#     return render(request,'agent_dashboard.html',{'tickets':tickets,'agent':agent})

def agent_dashboard(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:

            agent = Agent.objects.get(username=username, password=password)

            request.session['agent_id'] = agent.id


            tickets = Ticket.objects.filter(assigned_agent=agent)
            return render(request, 'agent_dashboard.html', {
                'tickets': tickets,
                'agent': agent
            })

        except Agent.DoesNotExist:
            messages.error(request, "Invalid username or password.")
            return redirect('login')

    else:
        # If already logged in
        agent_id = request.session.get('agent_id')
        if agent_id:
            agent = Agent.objects.get(id=agent_id)
            tickets = Ticket.objects.filter(assigned_agent=agent)
            return render(request, 'agent_dashboard.html', {
                'tickets': tickets,
                'agent': agent
            })
        else:
            return redirect('login')

        
def update_ticket(request,tid):
    agent_id=request.session.grt('agent_id')
    if not agent_id:
        return redirect(login)
    agent=Agent.objects.get(id=agent_id)
    ticket=Ticket.objects.get(id=tid,assigned_agent=agent)
    if request.method=='POST':
        ticket.status='closed'
        ticket.save()
        return redirect(agent_dashboard)
    return render(request,'update_ticket.html',{'ticket':ticket})

def logout_agent(request):
    agent_id = request.session.get('agent_id')
    if agent_id:
        agent = Agent.objects.get(id=agent_id)
        agent.is_available = False
        agent.save()
        del request.session['agent_id']

    return redirect('login_agent')