from django.shortcuts import render, redirect
from django.contrib import messages
from agents.models import Agent
from tickets.models import Ticket
from django.contrib.auth import logout
from django.utils import timezone
from django.core.mail import send_mail
from django.db.models import F, Value
from django.db import transaction
from django.db.models.functions import Coalesce
from django.db.models import Q

# ---------------- Helper: Fair available-agent picker ---------------- #
def get_next_available_agent():
    return (
        Agent.objects.filter(is_available=True)
        .annotate(
            # Replace NULL last_assigned with a very old date for fair ordering
            sort_time=Coalesce('last_assigned', Value(timezone.datetime(2000, 1, 1, tzinfo=timezone.utc)))
        )
        .order_by('sort_time', 'id')
        .first()
    )
    


# ---------------- Agent Home & Login ---------------- #
def agenthome(request):
    return render(request, 'agenthome.html')


def login(request):
    return render(request, 'login.html')


def agent_dashboard(request):
    """
    Handles agent login and dashboard display.
    - Marks agent as available upon login.
    - Assigns an unassigned open ticket directly to the logging-in agent (if any).
    - Case-insensitive status checks.
    - Uses transaction locking to prevent race conditions.
    """
    if request.method == 'POST':
        username = request.POST.get('email')
        password = request.POST.get('password')

        try:
            agent = Agent.objects.get(email=username, password=password)

            # Mark agent available
            agent.is_available = True
            agent.save()

            # Check if the agent already has an open ticket
            active_ticket = Ticket.objects.filter(
                assigned_agent=agent, status__iexact='open'
            ).first()

            # If no active ticket, try to assign one
            if not active_ticket:
                with transaction.atomic():
                    # Safely fetch the oldest unassigned open ticket
                    unassigned_ticket = (
                        Ticket.objects.select_for_update(skip_locked=True)
                        .filter(assigned_agent__isnull=True, status__iexact='open')
                        .order_by('created_at')
                        .first()
                    )

                    if unassigned_ticket:
                        # Assign directly to this agent
                        unassigned_ticket.assigned_agent = agent
                        unassigned_ticket.save()

                        # Update agent availability & timestamp
                        agent.is_available = False
                        agent.last_assigned = timezone.now()
                        agent.save()

                        # Notify the ticket creator
                        send_mail(
                            subject=f"Ticket '{unassigned_ticket.title}' Assigned",
                            message=f"Your ticket '{unassigned_ticket.title}' "
                                    f"has been assigned to agent {agent.name}.",
                            from_email=None,
                            recipient_list=[unassigned_ticket.email],
                            fail_silently=False,
                        )

            # Store session and render dashboard
            request.session['agent_id'] = agent.id
            tickets = Ticket.objects.filter(assigned_agent=agent)
            return render(request, 'agent_dashboard.html', {'tickets': tickets, 'agent': agent})

        except Agent.DoesNotExist:
            messages.error(request, "Invalid username or password.")
            return redirect('login')

    else:
        # Already logged-in agent
        agent_id = request.session.get('agent_id')
        if agent_id:
            agent = Agent.objects.get(id=agent_id)

            # If agent has no active ticket, assign one if available
            active_ticket = Ticket.objects.filter(
                assigned_agent=agent, status__iexact='open'
            ).first()

            if not active_ticket:
                with transaction.atomic():
                    unassigned_ticket = (
                        Ticket.objects.select_for_update(skip_locked=True)
                        .filter(assigned_agent__isnull=True, status__iexact='open')
                        .order_by('created_at')
                        .first()
                    )

                    if unassigned_ticket:
                        unassigned_ticket.assigned_agent = agent
                        unassigned_ticket.save()

                        agent.is_available = False
                        agent.last_assigned = timezone.now()
                        agent.save()

                        send_mail(
                            subject=f"Ticket '{unassigned_ticket.title}' Assigned",
                            message=f"Your ticket '{unassigned_ticket.title}' "
                                    f"has been assigned to agent {agent.name}.",
                            from_email=None,
                            recipient_list=[unassigned_ticket.email],
                            fail_silently=False,
                        )

            tickets = Ticket.objects.filter(assigned_agent=agent)
            return render(request, 'agent_dashboard.html', {'tickets': tickets, 'agent': agent})
        else:
            return redirect('login')


def update_ticket(request, tid):
    """
    When an agent closes a ticket:
    - Mark it as 'Closed'
    - Mark the agent as available again
    - Safely assign the next unassigned open ticket (if any)
    """
    agent_id = request.session.get('agent_id')
    if not agent_id:
        return redirect('login')

    agent = Agent.objects.get(id=agent_id)
    ticket = Ticket.objects.get(id=tid, assigned_agent=agent)

    if request.method == 'POST':
        # 1️⃣ Close the ticket
        ticket.status = 'Closed'
        ticket.save()

        # 2️⃣ Mark this agent as available again
        agent.is_available = True
        agent.save()

        # 3️⃣ Notify the user
        send_mail(
            subject=f"Ticket '{ticket.title}' Resolved",
            message=f"Your ticket '{ticket.title}' has been resolved by {agent.name}. "
                    f"Thank you for your patience!",
            from_email=None,
            recipient_list=[ticket.email],
            fail_silently=False,
        )

        # 4️⃣ Safely assign the next open ticket (if any)
        with transaction.atomic():
            next_ticket = (
                Ticket.objects.select_for_update(skip_locked=True)
                .filter(assigned_agent__isnull=True, status__iexact='open')
                .order_by('created_at')
                .first()
            )

            if next_ticket:
                # Get the next available agent (fairness)
                next_agent = get_next_available_agent()

                # If none are available, reassign to the current agent
                if not next_agent:
                    next_agent = agent

                next_ticket.assigned_agent = next_agent
                next_ticket.save()

                next_agent.is_available = False
                next_agent.last_assigned = timezone.now()
                next_agent.save()

                send_mail(
                    subject=f"Ticket '{next_ticket.title}' Assigned",
                    message=f"Your ticket '{next_ticket.title}' "
                            f"has been assigned to agent {next_agent.name}.",
                    from_email=None,
                    recipient_list=[next_ticket.email],
                    fail_silently=False,
                )

        messages.success(request, f'Ticket "{ticket.title}" marked as closed.')
        return redirect('agent_dashboard')

    return render(request, 'update_ticket.html', {'ticket': ticket})



def logout_agent(request):
    """
    Logs out the agent and marks them unavailable.
    """
    agent_id = request.session.get('agent_id')
    if agent_id:
        agent = Agent.objects.get(id=agent_id)
        agent.is_available = False
        agent.save()
        logout(request)

    return redirect('login')
