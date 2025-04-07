from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100,blank=True)
    email = models.EmailField(blank=True)
    tagline = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=22,blank=True)
    name = models.CharField(max_length=100,blank=True)
    company_logo = models.ImageField(upload_to='profiles/',blank=True)
    
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True) 


    def __str__(self):
        return f"{self.user.username}'s Profile"
