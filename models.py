from django.db import models
from django.contrib.auth.models import User

class StudyPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject_name = models.CharField(max_length=100)
    hours_allocated = models.FloatField()
    due_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.subject_name


class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, default='General')
    title = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.subject} - {self.title}"
   