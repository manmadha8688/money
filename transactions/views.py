from django.shortcuts import render
from loans.models import LoanRequest

from django.db.models import Q
def all_transactions(request):
    lender = request.user  # current lender

    loans = (
        LoanRequest.objects
        .filter(lender=lender).filter(Q(status="paymentdone") | Q(status="paymentreceived"))
        .select_related('payment', 'borrower')
        .prefetch_related('status_history')
        .order_by('-updated_at')
    )
    payment_done = {}

    for loan in loans:
      for history in loan.status_history.all():
          if history.status == 'paymentdone':
              payment_done[loan.id] = history.updated_at
    
    context = {
    'loans': loans,
    'payment_done': payment_done,
    }
    
    return render(request, 'transactions/all_transactions.html',context)
