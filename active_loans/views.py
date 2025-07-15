from django.shortcuts import render,redirect,get_object_or_404
from loans.models import LoanRequest
from django.db.models import Q
from loans.views import get_installment_schedule
from .models import ReturnPayment,ActiveLoan
from datetime import timedelta,datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from django.urls import reverse

from loans.views import apply_filter

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect

from django.utils import timezone
# Create your views here.
@login_required
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

@login_required
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

@login_required
def onetime_loans(request):
    loans = LoanRequest.objects.filter(lender=request.user ,status="paymentreceived" , payment_plan="daily",activeloan__status__in=["overdue", "Repaying"]).select_related(
        'lender__active_user',
        'borrower',
        'payment',
        'activeloan'  
    ).prefetch_related(
        'activeloan__return_payments'
    ).order_by('id')
    
    return render(request,'active_loans/onetimeloans.html',{"loans" : loans})

@login_required
def all_loans(request):
    if request.method == "POST":
        id = request.POST.get('loan_id')
        activeloan = ActiveLoan.objects.select_related('loan_request').prefetch_related('return_payments').get(id=id)

        amount = request.POST.get('amount')
        amount = Decimal(amount)
        payment_method = request.POST.get('method')
        utr = request.POST.get('utr', '')
        cash_person = request.POST.get('cash_person', '')
        payment_app = request.POST.get('platform', '')

        due_date = datetime.strptime(request.POST["due_date"], "%Y-%m-%d").date()
        existing_payment = next(
            (p for p in activeloan.return_payments.all() if p.due_date == due_date),
            None
            )

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
                activeloan.next_due_date = None
                activeloan.save()
                return redirect(f"{reverse('all-loans')}?paidpayment=true&loan_id={activeloan.loan_request.id}&amount={amount}")
                
            
            
            if  activeloan.loan_request.payment_plan == 'weekly':
                activeloan.next_due_date = payment.due_date + timedelta(weeks=1)
            elif activeloan.loan_request.payment_plan  == "daily":
                activeloan.next_due_date = payment.due_date + timedelta(days=1)

            activeloan.save()
            return redirect(f"{reverse('all-loans')}?paidpayment=true&loan_id={activeloan.loan_request.id}&amount={amount}")
        elif activeloan.loan_request.payment_plan == "monthly" :
            
                payment, created = ReturnPayment.objects.get_or_create(
                    returnloan=activeloan,
                    due_date=due_date,
                    amount=amount,
                    payment_method=payment_method,
                    utr=utr,
                    status ="pending",
                    cash_person=cash_person,
                    payment_app=payment_app,
                )
                if created:
                    activeloan.total_paid += payment.amount
            
                    activeloan.remaining_balance -= payment.amount
                    activeloan.last_payment_date = payment.due_date

                    if activeloan.remaining_balance == 0 :
                        activeloan.status = 'closed'
                        activeloan.next_due_date = None
                        activeloan.save()
                        return redirect(f"{reverse('all-loans')}?paidpayment=true&loan_id={activeloan.loan_request.id}&amount={amount}")

                    activeloan.save()
                    return redirect(f"{reverse('all-loans')}?paidpayment=true&loan_id={activeloan.loan_request.id}&amount={amount}")
           
                    
                else:
                    return redirect(f"{reverse('all-loans')}?paymentexists=true")
                

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

@login_required
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



@login_required
def repayment_confirmation(request):
    pending_payments = ReturnPayment.objects.filter(
    status='pending',
    returnloan__loan_request__lender=request.user
    ).select_related(
    'returnloan__loan_request__borrower',
    'returnloan'
    )
    return render(request,'repayment_confirmation.html',{'return_payments':pending_payments})

@login_required
def update_repayment_status(request):
    if request.method == 'POST':
        payment_id = request.POST.get('payment_id')
        confirm = request.POST.get('confirm', 'false')
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
        
        loan = payment.returnloan.loan_request
        if action == 'paid':
            

                
                active_loan = payment.returnloan
                active_loan.last_payment_date = payment.due_date

                active_loan.total_paid += payment.amount
                active_loan.remaining_balance -= payment.amount
                payment.status = 'success'
                
                payment.save()
                
                if active_loan.remaining_balance == 0 :
                    active_loan.status = 'closed'
                    active_loan.next_due_date = None
                    if loan.payment_plan =="weekly":
                        active_loan.next_due_date += timedelta(weeks=week + 1)                                          
                    active_loan.save()
                    return redirect(f"{reverse('repayment-confirmation')}?paid=true&loan_id={loan.id}&amount={payment.amount}")
            
                

                if  loan.payment_plan == 'weekly':
                    active_loan.next_due_date = payment.due_date + timedelta(weeks=1)
                elif loan.payment_plan == "daily":
                    active_loan.next_due_date = payment.due_date + timedelta(days=1)
                
                active_loan.save()
                return redirect(f"{reverse('repayment-confirmation')}?paid=true&loan_id={loan.id}&amount={payment.amount}")
            
        elif action == 'not_paid':
            payment.delete()
            return redirect(f"{reverse('repayment-confirmation')}?paid=false&loan_id={loan.id}&amount={payment.amount}")
                
                

    return redirect('repayment-confirmation')

from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404

def check_duplicate_payment(request, payment_id):
    if not request.method == "GET":
        raise Http404("Only GET allowed")

    try:
        payment = get_object_or_404(ReturnPayment, id=payment_id)

        duplicate = ReturnPayment.objects.filter(
            returnloan=payment.returnloan,
            due_date=payment.due_date,
            amount=payment.amount,
            payment_method=payment.payment_method,
            utr=payment.utr,
            cash_person=payment.cash_person,
            payment_app=payment.payment_app,
            status='success'
        ).exists()

        return JsonResponse({'duplicate': duplicate})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



@login_required
def update_due_dates(request):
    today = timezone.now().date()
    active_loans = ActiveLoan.objects.filter(status='Repaying').select_related('loan_request').prefetch_related('return_payments')

    for loan in active_loans:
        previous_due_date = loan.next_due_date
        
        repayment_exists = any(
            rp.due_date == previous_due_date and rp.status == 'success'
            for rp in loan.return_payments.all()
            )
        if (previous_due_date < today) :

            if not repayment_exists :
                loan.status = 'overdue'
            
            elif loan.loan_request.payment_plan == 'monthly' :
                loan.next_due_date += relativedelta(months=1)
            
            loan.save()

    return redirect('dashboard')  # or wherever you want to redirect
