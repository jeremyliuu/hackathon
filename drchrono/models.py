from django.db import models

# Add your models here
class WaitingDuration(models.Model):
    """
    Local model in database.
    Save arrived time and get waiting time in each appointment.
    """
    app_id = models.CharField(max_length=255, unique=True)
    arrived_time = models.DateTimeField(auto_now_add=False, null=True, blank=True, default=None)
    start_time = models.DateTimeField(auto_now_add=False, null=True, blank=True, default=None)




