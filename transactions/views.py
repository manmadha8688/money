from django.shortcuts import render
from loans.models import LoanRequest
from loans.views import apply_filter
from django.db.models import Q

from django.utils.dateparse import parse_date
def all_transactions(request):
    lender = request.user  # current lender

    loans = LoanRequest.objects.filter(lender=lender ,status="paymentreceived").order_by('-updated_at')
    if request.method == "GET":
        from_date = request.GET.get('from_date', '').strip()
        to_date = request.GET.get('to_date', '').strip()

        loans = apply_filter(loans,request)
        if from_date:
            loans = loans.filter(
            Q(status_history__updated_at__date__gte=parse_date(from_date)) & Q(status_history__status="paymentdone"))
        print(loans.count())
        if to_date:
            loans = loans.filter(
           Q(status_history__updated_at__date__lte=parse_date(to_date)) & Q(status_history__status="paymentdone"))
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
