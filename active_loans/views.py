from django.shortcuts import render,redirect
from loans.models import LoanRequest
from django.db.models import Q
from loans.views import get_installment_schedule
from .models import ReturnPayment,ActiveLoan
from datetime import timedelta,datetime
from dateutil.relativedelta import relativedelta
from django.shortcuts import get_object_or_404
from decimal import Decimal
from django.urls import reverse

from loans.views import apply_filter
# Create your views here.
def montly_loans(request):

    loans = LoanRequest.objects.filter(lender=request.user ,status="paymentreceived",payment_plan="monthly",activeloan__status__in=["overdue", "Repaying"]).select_related(
        'lender__active_user',
        'borrower',
        'payment',
        'activeloan'  
    ).prefetch_related(
        'activeloan__return_payments'
    ).order_by('id')
    return render(request,'active_loans/montlyloans.html',{"loans" : loans})

def weekly_loans(request):
    loans = LoanRequest.objects.filter(lender=request.user ,status="paymentreceived", payment_plan="weekly",activeloan__status__in=["overdue", "Repaying"]).select_related(
        'lender__active_user',
        'borrower',
        'payment',
        'activeloan'  
    ).prefetch_related(
        'activeloan__return_payments'
    ).order_by('id')
    
    for loan in loans:
        loan.schedule = get_installment_schedule(loan)

    return render(request,'active_loans/weeklyloans.html',{"loans" : loans})

def onetime_loans(request):
    loans = LoanRequest.objects.filter(lender=request.user ,status="paymentreceived" , payment_plan="onetime",activeloan__status__in=["overdue", "Repaying"]).select_related(
        'lender__active_user',
        'borrower',
        'payment',
        'activeloan'  
    ).prefetch_related(
        'activeloan__return_payments'
    ).order_by('id')
    
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

        due_date = datetime.strptime(request.POST["due_date"], "%Y-%m-%d").date()
        existing_payment = ReturnPayment.objects.filter(
            returnloan=activeloan,
            due_date=due_date, # optionally filter by pending only
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

            if activeloan.remaining_balance == 0 :
                activeloan.status = 'closed'
                if  ctiveloan.loan_request.payment_plan == 'weekly':
                    activeloan.next_due_date = None
                elif activeloan.loan_request.payment_plan  == 'monthly':
                    activeloan.next_due_date = None
                activeloan.save()
                return redirect(f"{reverse('all-loans')}?paidpayment=true&loan_id={activeloan.loan_request.id}&amount={amount}")
            
            
            if  activeloan.loan_request.payment_plan == 'weekly':
                activeloan.next_due_date = payment.due_date + timedelta(weeks=1)
            elif activeloan.loan_request.payment_plan  == 'monthly':
                activeloan.next_due_date = payment.due_date + relativedelta(months=1)
            activeloan.save()
            
            return redirect(f"{reverse('all-loans')}?paidpayment=true&loan_id={activeloan.loan_request.id}&amount={amount}")
            
        else:
            return redirect(f"{reverse('all-loans')}?paymentexists=true")

            
    loans = LoanRequest.objects.filter(lender=request.user ,status="paymentreceived",activeloan__status__in=["overdue", "Repaying"]).select_related(
        'lender__active_user',
        'borrower',
        'payment',
        'activeloan'  
    ).prefetch_related(
        'activeloan__return_payments'
    ).order_by('id')

    if request.method == "GET":
        loans = apply_filter(loans, request)

    for loan in loans:
        if loan.payment_plan == "weekly":

            loan.schedule = get_installment_schedule(loan)
    

    return render(request,'active_loans/all_loans.html',{"loans" : loans})

def closed_loans(request):
    loans = LoanRequest.objects.filter(lender=request.user ,status="paymentreceived",activeloan__status="closed").select_related(
        'lender__active_user',
        'borrower',
        'payment',
        'activeloan'  
    ).prefetch_related(
        'activeloan__return_payments'
    ).order_by('id')
    for loan in loans:
        if loan.payment_plan == "weekly":

            loan.schedule = get_installment_schedule(loan)
    

    return render(request,'closed_loans.html',{"loans" : loans})




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
                 

                loan = payment.returnloan.loan_request
                active_loan = payment.returnloan
                active_loan.last_payment_date = payment.due_date

                active_loan.total_paid += payment.amount
                active_loan.remaining_balance -= payment.amount
                payment.status = 'success'
                
                payment.save()
                
                if active_loan.remaining_balance == 0 :
                    active_loan.status = 'closed'
                    if  loan.payment_plan == 'weekly':
                        active_loan.next_due_date = None
                    elif loan.payment_plan  == 'monthly':
                        active_loan.next_due_date = None
                    active_loan.save()
                    return redirect(f"{reverse('repayment-confirmation')}?paid=true&loan_id={loan.id}&amount={payment.amount}")
            
                

                if  loan.payment_plan == 'weekly':
                    active_loan.next_due_date = payment.due_date + timedelta(weeks=1)
                elif loan.payment_plan  == 'monthly':
                    active_loan.next_due_date = payment.due_date + relativedelta(months=1)
                active_loan.save()
                return redirect(f"{reverse('repayment-confirmation')}?paid=true&loan_id={loan.id}&amount={payment.amount}")
            
        elif action == 'not_paid':
            print('not paid')
            return redirect(f"{reverse('repayment-confirmation')}?paid=false")
                
                

    return redirect('repayment-confirmation')