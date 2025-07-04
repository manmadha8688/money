from django.db import models

# Create your models here.
# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
class CustomUser(AbstractUser):
    # Add custom fields if you want, optional
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
