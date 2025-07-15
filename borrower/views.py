from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash,logout
from django.contrib.auth import get_user_model
User = get_user_model()

import random
from django.shortcuts import render, redirect
from django.contrib import messages
from active_loans.models import ActiveLoan,ReturnPayment
from datetime import datetime ,timedelta
from django.urls import reverse
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from loans.views import get_installment_schedule
from loans.models import LoanRequest

import string
from django.http import JsonResponse
@login_required
def change_client_password(request):
    if request.method == "POST":
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
        elif len(new_password) < 6:
            messages.error(request, "Password must be at least 6 characters.")
        else:
            user = User.objects.select_related('borrower').get(id=request.user.id)
            user.set_password(new_password)
            user.last_name = ""
            user.borrower.passcode = ""  # unset first-login flag
            user.save()
            user.borrower.save()
            update_session_auth_hash(request, user)  # keep the user logged in
            messages.success(request, "You’ve successfully logged in and your password has been changed.")
            
            return redirect('client-dashboard') 

    return render(request,'borrower/change_password.html')

def client_forgot_password(request):
    if request.method == "POST":
        username = request.POST.get("username")

        try:
            user = User.objects.select_related('borrower').get(username=username)

            passcode = str(random.randint(100000, 999999))
            user.set_password(passcode)
            user.last_name = "true"
            user.borrower.passcode = passcode
            
            user.borrower.save()
            user.save()
            messages.success(request, f"A temporary password has been set. Contact your lender to retrieve it.")
            return redirect('client-login')
        except User.DoesNotExist:
            messages.error(request, "Username not found. Please check and try again.")

    return render(request,'borrower/forgot_password.html')

@login_required
def client_pass_code(request):
    
    clients = User.objects.select_related('borrower').filter(
        last_name="true",
        borrower__passcode__isnull=False  
        )
    
    return render(request,'client_pass_code.html',{'clients':clients})

@login_required
def client_dashboard(request):
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
                )
            payment.save()
             
            messages.success(request,'You have successfully submitted your payment. Your lender will review and confirm it shortly.')
            return redirect(f"{reverse('client-dashboard')}")

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
                    messages.success(request, 'You have successfully submitted your payment. Your lender will review and confirm it shortly.')
                else:
                    messages.error(request,'This Payment is already done and is under confirmation.')
                return redirect(f"{reverse('client-dashboard')}")
        else:
            messages.error(request,'Payment for this due date is already done and is under confirmation.')
            return redirect(f"{reverse('client-dashboard')}")

    user = request.user
    all_loans = user.client_loans.select_related(
        'borrower',
        'payment',
        'activeloan'
    ).prefetch_related(
        'activeloan__return_payments'
    ).filter(
        submitted=True
    )

# Now split in Python
    borrowed_loans = [loan for loan in all_loans if loan.status == "paymentreceived"]
    pending_loans = [loan for loan in all_loans if loan.status != "paymentreceived"]

    count = len(borrowed_loans)
    """
    if count==0:
        logout(request)
        return redirect(f"{reverse('client-login')}?user=false")
    """
    total ,paid , remaining = 0 ,0 ,0
    for loan in borrowed_loans:

        loan.return_payments = loan.activeloan.return_payments.all()

        loan.mini = loan.instalment
        loan.maxi = loan.activeloan.remaining_balance
        loan.percentage = round((loan.activeloan.total_paid / (loan.amount + loan.interest_amount)) * 100 , 2)
        total += loan.amount
        paid += loan.activeloan.total_paid
        remaining += loan.activeloan.remaining_balance
        if loan.payment_plan == "weekly":
            
            loan.schedule = get_installment_schedule(loan)
        if loan.payment_plan == "monthly":
            payment_done = loan.activeloan.return_payments.filter(
                due_date=loan.activeloan.next_due_date,
                status='success'
            ).exists()

            if payment_done:
                loan.mini = 0
    
    lender = request.user.lender

    return render(request,'borrower/loan_details.html',
    {'loans':borrowed_loans ,
     'pending_loans':pending_loans,
     "lender":lender ,
      'count':count,
      'total':total,
      'paid':paid,
      'remaining':remaining
      }
      )

@login_required
def client_new_loan(request):
    client = request.user
    loan = LoanRequest.objects.filter(client=client,submitted=False).first()

    if loan is None:
        unique_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))

        loan = LoanRequest.objects.create(
            lender=client.lender,
            unique_id=unique_id,
            client = client,
            borrower = client.borrower,
            submitted=False,
            amount=0,
        )
    else:
        return redirect('new-loan', lender_id=loan.lender.id, unique_id=loan.unique_id)
        
    return redirect('new-loan', lender_id=loan.lender.id, unique_id=loan.unique_id)

