from django.shortcuts import render
from loans.models import LoanRequest
from loans.views import apply_filter
from django.db.models import Q
from django.utils.dateparse import parse_date

from active_loans.models import ReturnPayment
from itertools import chain


def all_transactions(request):
    lender = request.user

    from_date = parse_date(request.GET.get('from_date', ''))
    to_date = parse_date(request.GET.get('to_date', ''))

    loans = LoanRequest.objects.filter(
        lender=lender,
        status__in=["paymentdone", "paymentnotreceived", "paymentreceived"]
    ).select_related('payment', 'borrower', 'activeloan') \
     .prefetch_related('status_history', 'activeloan__return_payments') \
     .order_by('-updated_at')

    if request.method == "GET":
        loans = apply_filter(loans, request)

    # Set entry_type and done_at
    for loan in loans:
        loan.entry_type = 'loan'
        loan.done_at = None
        for history in loan.status_history.all():
            if history.status == 'paymentdone':
                loan.done_at = history.updated_at
                break

    # Filter loans by date
    if from_date:
        loans = [loan for loan in loans if loan.done_at and loan.done_at.date() >= from_date]
    if to_date:
        loans = [loan for loan in loans if loan.done_at and loan.done_at.date() <= to_date]

    # Collect return payments
    return_payments = []
    for loan in loans:
        if hasattr(loan, 'activeloan') and loan.activeloan:
            for rp in loan.activeloan.return_payments.all():
                rp.entry_type = 'return_payment'
                rp.done_at = rp.created_at
                return_payments.append(rp)

    # Filter return payments by date
    if from_date:
        return_payments = [rp for rp in return_payments if rp.done_at and rp.done_at.date() >= from_date]
    if to_date:
        return_payments = [rp for rp in return_payments if rp.done_at and rp.done_at.date() <= to_date]

    # Merge and sort
    merged_entries = sorted(
        chain(loans, return_payments),
        key=lambda x: x.done_at,
        reverse=True
    )

    return render(request, 'transactions/all_transactions.html', {
        'loans': merged_entries,
    })
