from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash,logout
from django.contrib.auth.models import User
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
            user = request.user
            user.set_password(new_password)
            user.last_name = "borrower"  # unset first-login flag
            user.save()
            update_session_auth_hash(request, user)  # keep the user logged in
            messages.success(request, "You’ve successfully logged in and your password has been changed.")
            
            return redirect('client-dashboard') 

    return render(request,'borrower/change_password.html')

def client_forgot_password(request):
    if request.method == "POST":
        username = request.POST.get("username")

        try:
            user = User.objects.get(username=username)

            passcode = str(random.randint(100000, 999999))
            user.set_password(passcode)
            user.last_name = "true"
            print(passcode)
            user.save()
            messages.success(request, f"A temporary password has been set. Contact your lender to retrieve it.")
            return redirect('client-login')
        except User.DoesNotExist:
            messages.error(request, "Username not found. Please check and try again.")

    return render(request,'borrower/forgot_password.html')

def client_pass_code(request):
    flagged_users = User.objects.filter(last_name="true")

    clients = []
    for client in flagged_users:
        if client.check_password("client@123"):
            continue  # skip if password is still default
        if LoanRequest.objects.filter(client=client, lender=request.user).exists():
            clients.append(client)

    return render(request,'client_pass_code.html',{'clients':clients})


def client_dashboard(request):
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
                )
            payment.save()
             
            messages.success(request,'You have successfully submitted your payment. Your lender will review and confirm it shortly.')
            return redirect(f"{reverse('client-dashboard')}")
            
        else:
            
            messages.error(request,'already done')
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
            loan.mini = loan.interest_amount
    
    lender = borrowed_loans[0].lender

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

import random
import string
from django.http import JsonResponse

def client_new_loan(request):
    client = request.user
    loan = LoanRequest.objects.filter(client=client,submitted=False).first()

    if loan is None:
        previous_loan = LoanRequest.objects.filter(client=request.user, submitted=True).first()
        unique_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))

        loan = LoanRequest.objects.create(
            lender=previous_loan.lender,
            unique_id=unique_id,
            client = client,
            borrower = previous_loan.borrower,
            submitted=False,
            amount=0,
        )
    else:
        return redirect('new-loan', lender_id=loan.lender.id, unique_id=loan.unique_id)
        
    return redirect('new-loan', lender_id=loan.lender.id, unique_id=loan.unique_id)

