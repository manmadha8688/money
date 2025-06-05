from django.shortcuts import render,redirect
from loans.models import LoanRequest
from django.db.models import Q
from loans.views import get_installment_schedule
from .models import ReturnPayment
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from django.shortcuts import get_object_or_404
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

def repayment_confirmation(request):
    pending_payments = ReturnPayment.objects.filter(
    status='pending',
    returnloan__loan_request__lender=request.user
    ).select_related(
    'returnloan__loan_request__borrower',
    'returnloan'
    )
    return render(request,'repayment_confirmation.html',{'return_payments':pending_payments})

def update_repayment_status(request):
    if request.method == 'POST':
        payment_id = request.POST.get('payment_id')
        action = request.POST.get('action')  # either 'paid' or 'not_paid'
        
        payment = get_object_or_404(
        ReturnPayment.objects.select_related(
        'returnloan',  # ForeignKey
        'returnloan__loan_request',  # OneToOneField
        'returnloan__loan_request__borrower',
        'returnloan__loan_request__payment'
        ),
        id=payment_id
        )
        if action == 'paid':
                payment.status = 'success'
                payment.save()

                loan = payment.returnloan.loan_request
                active_loan = payment.returnloan
                
                print(active_loan.total_paid)
                active_loan.total_paid += payment.amount
                print(active_loan.total_paid)
                active_loan.remaining_balance -= payment.amount
                active_loan.last_payment_date = payment.due_date
                if  loan.payment_plan == 'weekly':
                    active_loan.next_due_date = payment.due_date + timedelta(weeks=1)
                elif loan.payment_plan  == 'monthly':
                    active_loan.next_due_date = payment.due_date + relativedelta(months=1)
                active_loan.save()
                
                
        elif action == 'not_paid':
                print('not paid')
                
                

        return redirect('repayment-confirmation')  

    return redirect('repayment-confirmation')