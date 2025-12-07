# cvs/models.py
from django.db import models
from django.contrib.auth.models import User

class CV(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    file = models.FileField(upload_to='cvs/')
    extracted_text = models.TextField(blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    skills = models.TextField(blank=True, null=True)
    education = models.TextField(blank=True, null=True)
    experience = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    score = models.FloatField(default=0)
    match_score = models.FloatField(default=0)
    potential_score = models.FloatField(default=0)

    def __str__(self):
        return f"CV của {self.full_name or 'Ứng viên'}"
    
class Job(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255, blank=True, null=True)
    url = models.URLField()
    labels = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=False)
    fetched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class CVJobMatch(models.Model):
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name='matches')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='matches')
    match_score = models.FloatField()
    matched_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('cv', 'job')
    def __str__(self):
        return f"{self.cv.full_name} - {self.job.title} ({self.match_score}%)"
