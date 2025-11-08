from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Agent(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    is_available = models.BooleanField(default=False)
    last_assigned=models.DateTimeField(null=True, blank=True)



    # def __str__(self):
    #     return self.name



