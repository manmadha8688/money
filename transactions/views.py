from django.shortcuts import render
from loans.models import LoanRequest
from loans.views import apply_filter
from django.db.models import Q

from django.utils.dateparse import parse_date
def all_transactions(request):
    lender = request.user
    loans = LoanRequest.objects.filter(
        lender=lender,
        status="paymentreceived"
    ).select_related('payment', 'borrower').prefetch_related('status_history').order_by('-updated_at')

    from_date = request.GET.get('from_date', '').strip()
    to_date = request.GET.get('to_date', '').strip()

    if from_date or to_date:
        from_date_obj = parse_date(from_date) if from_date else None
        to_date_obj = parse_date(to_date) if to_date else None

        filtered_loan_ids = LoanStatusHistory.objects.filter(
            status='paymentdone',
            updated_at__date__gte=from_date_obj if from_date_obj else datetime.date.min,
            updated_at__date__lte=to_date_obj if to_date_obj else datetime.date.max
        ).values_list('loan_id', flat=True)

        loans = loans.filter(id__in=filtered_loan_ids)

    # Add done_at to each loan using prefetched status_history
    for loan in loans:
        for history in loan.status_history.all():
            if history.status == 'paymentdone':
                loan.done_at = history.updated_at
                break  # only need the first one

    context = {
        'loans': loans,
    }

    return render(request, 'transactions/all_transactions.html', context)
