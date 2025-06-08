from django.shortcuts import render
from loans.models import LoanRequest
from loans.views import apply_filter
from django.db.models import Q
from django.utils.dateparse import parse_date

from active_loans.models import ReturnPayment
from itertools import chain

def all_transactions(request):
    lender = request.user

    loans = LoanRequest.objects.filter(
        lender=lender,
        status__in=["paymentdone", "paymentnotreceived","paymentreceived"]
    ).select_related('payment', 'borrower', 'activeloan') \
     .prefetch_related('status_history', 'activeloan__return_payments') \
     .order_by('-updated_at')
    print(loans)
    # Add date for sorting
    for loan in loans:
        loan.entry_type = 'loan'
        for history in loan.status_history.all():
            if history.status == 'paymentdone':
                loan.done_at = history.updated_at
                break
        
    
    # Collect return payments
    return_payments = []
    for loan in loans:
        if hasattr(loan, 'activeloan') and loan.activeloan:
            for rp in loan.activeloan.return_payments.all():
                rp.entry_type = 'return_payment'
                rp.done_at = rp.created_at  # so we can sort it
                return_payments.append(rp)
    
    # Merge and sort
    merged_entries = sorted(
        chain(loans, return_payments),
        key=lambda x: x.done_at,
        reverse=True
    )
    
   
    return render(request, 'transactions/all_transactions.html', {
        'loans': merged_entries,
    })
