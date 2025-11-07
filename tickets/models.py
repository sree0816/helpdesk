from django.db import models

# Create your models here.

from django.db import models

class Ticket(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    email = models.EmailField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    sla_hours = models.IntegerField(default=24)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    assigned_agent = models.ForeignKey('agents.Agent', null=True, blank=True, on_delete=models.SET_NULL)

    # def __str__(self):
    #     return self.title
