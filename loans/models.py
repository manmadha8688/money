from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Borrower(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

class PaymentDetail(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('online', 'Online'),
    ]

    ONLINE_METHODS = [
        ('phonepe', 'Phone Pay'),
        ('googlepay', 'Google Pay'),
        ('paytm', 'Paytm'),
        ('bank', 'Bank Account'),
    ]

    
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS)

    # For cash
    cash_from = models.CharField(max_length=255, blank=True, null=True)

    # For online
    online_method = models.CharField(max_length=20, choices=ONLINE_METHODS, blank=True, null=True)
    upi_number = models.CharField(max_length=100, blank=True, null=True)
    upi_screenshot = models.ImageField(upload_to='payment_screenshots/', blank=True, null=True)

    # For bank transfer
    account_number = models.CharField(max_length=30, blank=True, null=True)
    ifsc = models.CharField(max_length=20, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)

    utr = models.CharField(max_length=100, blank=True, null=True)  # For online
    person = models.CharField(max_length=100, blank=True, null=True)  # For cash
    bank= models.CharField(max_length=100, blank=True, null=True)  # For bank


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at =models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.loan.borrower.name} - {self.payment_type.title()}"

class LoanRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('cancelled','Cancelled'),
        ('paymentprocess','Paymentprocess'),
        ('paymentdone','Paymentdone'),
        ('paymentreceived','Paymentreceived'),
    )
    lender = models.ForeignKey(User, on_delete=models.CASCADE)
    borrower = models.ForeignKey(Borrower,null=True, on_delete=models.CASCADE) 
    payment = models.OneToOneField(PaymentDetail,on_delete=models.CASCADE,null=True) # Links to Borrower model
    unique_id = models.CharField(max_length=100, unique=True)
    loan_item = models.CharField(max_length=100,null=True)  # Loan security item
    amount = models.IntegerField(default=0)
    apply_date = models.DateTimeField(null=True, blank=True)
    taken_date = models.DateField(null=True)
    return_date = models.DateField(null=True)
    referral = models.CharField(max_length=255, blank=True, null=True)  # Optional referral
    reason = models.TextField(blank=True, null=True)  # Optional notes
    submitted = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    interest = models.DecimalField(max_digits=5, decimal_places=1, default=5.0 )
    
    remark = models.CharField(max_length=500,blank=True)

    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        creating = self.pk is None
        if not creating:
            old_instance = LoanRequest.objects.get(pk=self.pk)
            if old_instance.status != self.status:
                # Save status change history
                LoanStatusHistory.objects.create(
                    loan=self,
                    status=self.status
                )
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Loan - {self.borrower.name} ({self.amount})"

class LoanStatusHistory(models.Model):
    loan = models.ForeignKey(LoanRequest, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=30, choices=LoanRequest.STATUS_CHOICES)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.loan.id} - {self.get_status_display()} @ {self.updated_at.strftime('%Y-%m-%d %H:%M')}"


class LoanImage(models.Model):
    loan = models.ForeignKey(LoanRequest, on_delete=models.CASCADE, related_name='loan_item_images')
    image = models.ImageField(upload_to='loan_items_images/')    

