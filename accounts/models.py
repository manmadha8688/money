from django.db import models

# Create your models here.
# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
import random
import string
class CustomUser(AbstractUser):
    # Add custom fields if you want, optional
    user_id = models.CharField(max_length=4, unique=True, blank=True, null=True)
    user_type = models.CharField(max_length=20, choices=[
        ('client', 'Client'),
        ('lender', 'Lender')
    ], blank=True, null=True,  default='lender'
    )
    
    lender = models.ForeignKey(  # 👈 ForeignKey to another user (the lender)
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clients',
        limit_choices_to={'user_type': 'lender'},
        help_text="Lender assigned to this user (if client)"
        )
    borrower = models.ForeignKey(  # 👈 ForeignKey to another user (the lender)
        'loans.Borrower',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clients',
        limit_choices_to={'user_type': 'lender'},
        help_text="Lender assigned to this user (if client)"
        )
        
        
    
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username
    
    def generate_user_id(self):
        first_letter = self.first_name[0].upper() if self.first_name else random.choice(string.ascii_uppercase)
        phone_digit = self.borrower.phone[-1] if hasattr(self, 'phone') and self.borrower.phone and self.borrower.phone[-1].isdigit() else random.choice(string.digits)
        rand_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=2))
        return f"{first_letter}{phone_digit}{rand_chars}"

    def save(self, *args, **kwargs):
        if not self.user_id:
            while True:
                uid = self.generate_user_id()
                if not CustomUser.objects.filter(user_id=uid).exists():
                    self.user_id = uid
                    break
        super().save(*args, **kwargs)