from django.shortcuts import render
from loans.models import LoanRequest
from django.db.models import Q
from loans.views import get_installment_schedule
# Create your views here.
def montly_loans(request):

    loans = LoanRequest.objects.filter(lender=request.user ,status="paymentreceived",payment_plan="monthly").select_related('activeloan','borrower')
    
    return render(request,'active_loans/montlyloans.html',{"loans" : loans})

def weekly_loans(request):
    loans = LoanRequest.objects.filter(lender=request.user ,status="paymentreceived", payment_plan="weekly").select_related('activeloan','borrower')
    for loan in loans:
        loan.schedule = get_installment_schedule(loan)

    return render(request,'active_loans/weeklyloans.html',{"loans" : loans})

def onetime_loans(request):
    loans = LoanRequest.objects.filter(lender=request.user ,status="paymentreceived" , payment_plan="onetime").select_related('activeloan','borrower')
    
    return render(request,'active_loans/onetimeloans.html',{"loans" : loans})

def all_loans(request):
    loans = LoanRequest.objects.filter(lender=request.user ,status="paymentreceived").select_related('activeloan','borrower')
    for loan in loans:
        if loan.payment_plan == "weekly":

            loan.schedule = get_installment_schedule(loan)

    return render(request,'active_loans/all_loans.html',{"loans" : loans})