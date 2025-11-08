from django.shortcuts import render,redirect
from agents.models import Agent
from django.db.models import Count, Avg, F, Q
from tickets.models import Ticket
from django.utils import timezone
import json
from datetime import timedelta



# Create your views here.
def adminhome(request):
    return render(request,'homeadmin.html')



# def dashboard(request):
#     tickets = Ticket.objects.all()
#
#     # ----- Status counts (normalize to lowercase to avoid duplicates) -----
#     status_counts_dict = {}
#     for t in tickets:
#         status = t.status.lower()  # normalize
#         status_counts_dict[status] = status_counts_dict.get(status, 0) + 1
#
#     status_counts = [{'status': k.capitalize(), 'count': v} for k, v in status_counts_dict.items()]
#
#     # ----- Agent performance (include all agents, even 0 closed tickets) -----
#     agents = Agent.objects.all().annotate(
#         closed_count=Count('ticket', filter=Q(ticket__status__iexact='closed'))
#     )
#     agent_performance = [{'assigned_agent__name': a.name, 'closed_count': a.closed_count} for a in agents]
#
#     # ----- Average resolution time for closed tickets -----
#     avg_resolution_time = (
#         tickets.filter(status__iexact='closed')
#         .annotate(res_time=(F('updated_at') - F('created_at')))
#         .aggregate(avg_time=Avg('res_time'))['avg_time']
#     )
#
#     context = {
#         'total_tickets': tickets.count(),
#         'open_tickets': tickets.filter(status__iexact='open').count(),
#         'closed_tickets': tickets.filter(status__iexact='closed').count(),
#         'pending_tickets': tickets.filter(status__iexact='pending').count(),
#         'avg_resolution_time': avg_resolution_time,
#         'status_counts_json': json.dumps(status_counts),
#         'agent_performance_json': json.dumps(agent_performance),
#     }
#
#     return render(request, 'dashboard.html', context)

# adminapp/views.py


# def dashboard(request):
#     tickets = Ticket.objects.all()
#     now = timezone.now()
#
#     # -------------------- SLA BREACH LOGIC --------------------
#     sla_limits = {
#         'high': timedelta(minutes=1),
#         'medium': timedelta(minutes=4),
#         'low': timedelta(hours=1),
#     }
#
#     sla_breached_tickets = 0
#     for ticket in tickets:
#         allowed_time = sla_limits.get(ticket.priority, timedelta(days=2))
#         # compute breach dynamically
#         ticket.sla_breached = (
#             ticket.status.lower() in ['open']
#             and (now - ticket.created_at) > allowed_time
#         )
#         if ticket.sla_breached:
#             sla_breached_tickets += 1
#     # -----------------------------------------------------------
#
#     # KPI data
#     status_counts = list(tickets.values('status').annotate(count=Count('status')))
#     if sla_breached_tickets > 0:
#         status_counts.append({'status': 'SLA Breached', 'count': sla_breached_tickets})
#
#     agent_performance = list(
#         tickets.filter(status='closed', assigned_agent__isnull=False)
#         .values('assigned_agent__name')
#         .annotate(closed_count=Count('id'))
#     )
#
#     avg_resolution_time = (
#         tickets.filter(status='closed')
#         .annotate(res_time=(F('updated_at') - F('created_at')))
#         .aggregate(avg_time=Avg('res_time'))['avg_time']
#     )
#
#     context = {
#         'tickets': tickets,
#         'status_counts_json': json.dumps(status_counts),
#         'agent_performance_json': json.dumps(agent_performance),
#         'total_tickets': tickets.count(),
#         'open_tickets': tickets.filter(status='open').count(),
#         'closed_tickets': tickets.filter(status='closed').count(),
#         'pending_tickets': tickets.filter(status='pending').count(),
#         'avg_resolution_time': avg_resolution_time,
#         'sla_breached_tickets': sla_breached_tickets,  # new KPI
#     }
#
#     return render(request, 'dashboard.html', context)

def dashboard(request):
    tickets = Ticket.objects.all()
    now = timezone.now()

    # -------------------- SLA BREACH LOGIC --------------------
    sla_limits = {
        'high': timedelta(minutes=1),
        'medium': timedelta(minutes=4),
        'low': timedelta(hours=1),
    }

    sla_breached_tickets = 0
    for ticket in tickets:
        allowed_time = sla_limits.get(ticket.priority, timedelta(days=2))
        ticket.sla_breached = (
            ticket.status.lower() == 'open' and (now - ticket.created_at) > allowed_time
        )
        if ticket.sla_breached:
            sla_breached_tickets += 1
    # -----------------------------------------------------------

    # KPI data
    status_counts = list(tickets.values('status').annotate(count=Count('status')))
    if sla_breached_tickets > 0:
        status_counts.append({'status': 'SLA Breached', 'count': sla_breached_tickets})

    # Include all agents (even with 0 closed tickets)
    agents = Agent.objects.all().annotate(
        closed_count=Count('ticket', filter=Q(ticket__status__iexact='closed'))
    )
    agent_performance = [
        {'name': a.name, 'closed_count': a.closed_count or 0}
        for a in agents
    ]

    # Average resolution time
    avg_resolution_time = (
        tickets.filter(status__iexact='closed')
        .annotate(res_time=(F('updated_at') - F('created_at')))
        .aggregate(avg_time=Avg('res_time'))['avg_time']
    )

    context = {
        'tickets': tickets,
        'status_counts_json': json.dumps(status_counts),
        'agent_performance_json': json.dumps(agent_performance),
        'total_tickets': tickets.count(),
        'open_tickets': tickets.filter(status__iexact='open').count(),
        'closed_tickets': tickets.filter(status__iexact='closed').count(),
        'pending_tickets': tickets.filter(status__iexact='pending').count(),
        'avg_resolution_time': avg_resolution_time,
        'sla_breached_tickets': sla_breached_tickets,
    }

    return render(request, 'dashboard.html', context)


def register(request):
    return render(request,'register.html')
def save_agent(request):
    if request.method=='POST':
        a=request.POST.get('name')
        b=request.POST.get('email')
        c=request.POST.get('password')
        obj=Agent(name=a,email=b,password=c,is_available='False')
        obj.save()
    return redirect(adminhome)



