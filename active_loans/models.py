from django.db import models
from loans.models import LoanRequest
# Create your models here.
class ActiveLoan(models.Model):
    loan_request = models.OneToOneField(LoanRequest, on_delete=models.CASCADE)

    # Status specific to active loan lifecycle
    status = models.CharField(max_length=20, choices=[
        ('repaying', 'Repaying'),
        ('overdue', 'Overdue'),
        ('closed', 'Closed'),
        ('defaulted', 'Defaulted')
    ], default='Repaying')

    # Repayment tracking
    total_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    remaining_balance = models.DecimalField(max_digits=10, decimal_places=2)
    next_due_date = models.DateField(null=True, blank=True)
    last_payment_date = models.DateField(null=True, blank=True)

    # Optional audit/tracking fields
    closed_date = models.DateField(null=True, blank=True)

    # Meta info
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.loan_request.id