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


class ReturnPayment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('online', 'Online'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
    ] 

    returnloan = models.ForeignKey(ActiveLoan, on_delete=models.CASCADE, related_name='return_payments')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    cash_person = models.CharField(max_length=100, blank=True, null=True)
    payment_app = models.CharField(max_length=50, blank=True, null=True)
    utr = models.CharField(max_length=50, blank=True, null=True)

    due_date = models.DateField(help_text="Due date of the installment")

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Return Payment ₹{self.amount} for Loan #{self.loan.id} ({self.method})"


    