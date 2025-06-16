from django.shortcuts import render,redirect
from loans.models import LoanRequest
from django.db.models import Q
from loans.views import get_installment_schedule
from .models import ReturnPayment,ActiveLoan
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from django.shortcuts import get_object_or_404
from decimal import Decimal
from django.urls import reverse
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
    if request.method == "POST":
        id = request.POST.get('loan_id')
        activeloan = ActiveLoan.objects.select_related('loan_request').get(id=id)

        amount = request.POST.get('amount')
        amount = Decimal(amount)
        payment_method = request.POST.get('method')
        utr = request.POST.get('utr', '')
        cash_person = request.POST.get('cash_person', '')
        payment_app = request.POST.get('platform', '')
        due_date = activeloan.next_due_date
                     
        existing_payment = ReturnPayment.objects.filter(
            returnloan=activeloan,
            due_date=due_date,
            status='pending'  # optionally filter by pending only
            ).first()

        if not existing_payment:
            payment = ReturnPayment(
                returnloan=activeloan,
                amount=amount,
                payment_method=payment_method,
                utr=utr,
                cash_person=cash_person,
                payment_app=payment_app,
                due_date=due_date,
                status='success'
                )
            payment.save()
            activeloan.total_paid += payment.amount
            
            activeloan.remaining_balance -= payment.amount
            activeloan.last_payment_date = payment.due_date
            if  activeloan.loan_request.payment_plan == 'weekly':
                activeloan.next_due_date = payment.due_date + timedelta(weeks=1)
            elif activeloan.loan_request.payment_plan  == 'monthly':
                activeloan.next_due_date = payment.due_date + relativedelta(months=1)
            activeloan.save()
            
        else:
            return redirect(f"{reverse('all-loans')}?paymentexists=true")

            
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
                
                active_loan.total_paid += payment.amount
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