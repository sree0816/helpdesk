 HELP DESK MANAGEMENT SYSTEM — PROJECT GUIDE



## PROJECT OVERVIEW

The Helpdesk Management System is a Django-based web application that automates ticket handling for a support team.
It includes intelligent ticket assignment, SLA breach detection, load balancing among agents, and an admin dashboard with performance analytics and visual reports.

The system simulates a real-world support workflow:
Ticket creation → Automatic assignment → Resolution → SLA monitoring → Administrative insights.

---

## APPLICATION STRUCTURE

1. **tickets** — Handles customer ticket creation, SLA tracking, and confirmation emails.
2. **agents** — Manages agent login, availability, automatic assignment, load balancing, and ticket resolution.
3. **adminapp** — Provides administrative dashboards, performance insights, and SLA breach analytics.

---

## FUNCTIONAL WORKFLOW

### 1. Ticket Creation (Customer Side)

**URL:** `/tickets/create/`
**App:** tickets

Customers fill out a simple form providing:

* Name
* Email
* Ticket Title
* Description
* Priority (High, Medium, or Low)

**Logic:**

* If any agent is available, the ticket is assigned instantly.
* If no agent is available, the ticket is stored as unassigned until an agent logs in.
* SLA time limits are based on ticket priority:

  * High: 1 minute
  * Medium: 4 minutes
  * Low: 1 hour
* The system sends an email confirmation to the customer and, if applicable, includes the assigned agent’s name.

**Concepts Demonstrated:**

* Form handling and model relationships
* Conditional logic for assignment
* Email integration using Django’s SMTP
* SLA tracking with datetime calculations

---

### 2. Agent Operations (Support Side)

**URL:** `/agents/login/`
**App:** agents

Agents can:

* Log in to mark themselves as available
* Automatically receive unassigned tickets
* Benefit from load balancing if all tickets are taken
* Close resolved tickets
* Log out to mark themselves unavailable

**Auto Assignment Process:**

1. When an agent logs in, they are marked as available.
2. The system checks for unassigned open tickets.
3. If found, the **oldest** unassigned ticket is assigned to that agent.
4. If there are no unassigned tickets, load balancing occurs.

**Load Balancing Logic:**

* The system looks for any agent who has **more than one** open ticket.
* The **newest** ticket from that overloaded agent is reassigned to the newly logged-in (or idle) agent.
* This ensures fair workload distribution without leaving any agent empty-handed.
* Customers are notified via email about the reassignment.

**When an Agent Closes a Ticket:**

* The ticket status is marked as Closed.
* The agent becomes available again.
* The next waiting or unassigned ticket is automatically assigned.
* The customer receives a resolution email.

**Concepts Demonstrated:**

* Agent availability tracking
* Database transactions with `transaction.atomic()` and `select_for_update()`
* Concurrency safety for multi-agent operations
* Dynamic email notifications
* Session management for agents

---

### 3. Admin Operations (Administrative Side)

**URL:** `/adminapp/dashboard/`
**App:** adminapp

Admins can view key performance indicators (KPIs), SLA breaches, and overall team activity.

**Dashboard Features:**

* Total, open, closed, and pending tickets
* SLA breach detection and counts
* Average resolution time
* Agent performance (tickets closed per agent)
* Visual charts (pie and bar charts using Chart.js)

**SLA Logic:**

* Each ticket’s resolution time is compared with SLA limits based on its priority.
* Tickets still open beyond their allowed time are marked as SLA breached.

**Agent Performance:**

* Displays total closed tickets per agent.
* Helps identify productivity and load patterns.

**Concepts Demonstrated:**

* Aggregations using Django ORM (`Count`, `Avg`, `Q`)
* JSON serialization for frontend charts
* Time-based SLA calculation
* Data visualization integration with Chart.js

---

## SLA MATRIX

| Priority | SLA Limit | Breach Condition             |
| -------- | --------- | ---------------------------- |
| High     | 1 minute  | Ticket open beyond 1 minute  |
| Medium   | 4 minutes | Ticket open beyond 4 minutes |
| Low      | 1 hour    | Ticket open beyond 1 hour    |

---

## TECHNICAL HIGHLIGHTS

* **Auto Ticket Assignment:** Uses fair round-robin logic based on `last_assigned` timestamps.
* **Load Balancing:** Moves the newest open ticket from the most-loaded agent (if they have more than one) to the newly logged-in agent.
* **Database Safety:** All assignments are handled within atomic transactions to avoid race conditions.
* **Email Notifications:** Sent at ticket creation, assignment, reassignment, and resolution.
* **SLA Tracking:** Automatically flags tickets that exceed their defined time limits.
* **Admin Dashboard:** Provides real-time visual analytics via Chart.js.
* **Agent Availability:** Agents are dynamically marked as available/unavailable during login and logout.
* **Case-insensitive Queries:** Ensures consistent matching for statuses such as “open”, “Open”, or “OPEN”.

---

## NAVIGATION MAP

| Role     | URL                       | Purpose                                       |
| -------- | ------------------------- | --------------------------------------------- |
| Customer | `/tickets/create/`        | Submit a new helpdesk ticket                  |
| Customer | `/tickets/createsuccess/` | View confirmation after ticket submission     |
| Agent    | `/agents/login/`          | Log in as support agent                       |
| Agent    | `/agents/dashboard/`      | View assigned tickets and close resolved ones |
| Admin    | `/adminapp/dashboard/`    | View KPIs, SLA breaches, and charts           |
| Admin    | `/adminapp/register/`     | Add or register new agents                    |

---

## REVIEWER TEST FLOW

1. **Customer Ticket Creation**

   * Visit `/tickets/create/` and submit a new ticket while no agent is logged in.
   * The ticket remains unassigned.

2. **Agent Login**

   * Log in from `/agents/login/`.
   * The unassigned ticket is automatically assigned.
   * If there are no unassigned tickets but another agent has multiple open ones, the newest ticket is moved to the new agent.

3. **Agent Ticket Closure**

   * On the dashboard, close a ticket.
   * The system marks it as Closed, sends a resolution email, and reassigns the next available ticket if one exists.

4. **Admin Dashboard**

   * Visit `/adminapp/dashboard/` to view ticket statistics, SLA breaches, and agent performance charts.

---

## EMAIL NOTIFICATIONS

| Event             | Recipient | Description                                                                  |
| ----------------- | --------- | ---------------------------------------------------------------------------- |
| Ticket Created    | Customer  | Confirms that a ticket was successfully submitted                            |
| Ticket Assigned   | Customer  | Informs which agent is handling the issue                                    |
| Ticket Reassigned | Customer  | Notifies that the ticket has been moved to a new agent for faster resolution |
| Ticket Closed     | Customer  | Confirms that the issue was resolved                                         |

---

## TECHNOLOGY STACK

| Category               | Tools Used                                                       |
| ---------------------- | ---------------------------------------------------------------- |
| Backend Framework      | Django 5.x                                                       |
| Database               | SQLite (development) / PostgreSQL (optional)                     |
| Frontend               | HTML5, CSS3, JavaScript, Chart.js                                |
| Email System           | Django SMTP + .env for configuration                           |
| Concurrency Control    | `transaction.atomic()` and `select_for_update(skip_locked=True)` |
| Environment Management | python-.env                                                    |
| Data Visualization     | Chart.js                                                         |

---

## DESIGN PRINCIPLES

1. Fairness: Ticket distribution ensures balanced workload among agents.
2. Safety: Uses database transactions to avoid conflicts during concurrent updates.
3. Scalability: Easily extendable for departments, escalations, and custom SLA rules.
4. Transparency: Provides complete visibility into system activity through dashboards.
5. Communication: Customers are notified at every step of the process.
6. The Django Admin panel (/admin/) can be used for direct database inspection.



## DEMONSTRATION SUMMARY

1. Customer submits a ticket → stored or auto-assigned.
2. Agent logs in → assigned or balanced ticket.
3. Agent closes ticket → status updated and next ticket assigned.
4. Admin monitors SLA and team performance through charts.


