from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from django.contrib import messages
from active_loans.models import ActiveLoan,ReturnPayment
from datetime import datetime ,timedelta
from django.urls import reverse
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from loans.views import get_installment_schedule
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
            user.last_name = ""  # unset first-login flag
            user.save()
            update_session_auth_hash(request, user)  # keep the user logged in
            messages.success(request, "Password changed successfully.")
            
            return redirect('client-dashboard')  

    return render(request,'borrower/change_password.html')

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
            
            messages.success(request,'success')
            return redirect(f"{reverse('client-dashboard')}")
            
        else:
            
            messages.error(request,'already done')
            return redirect(f"{reverse('client-dashboard')}")

    user = request.user
    borrowed_loans = user.client_loans.select_related(
        'borrower',
        'payment',
        'activeloan'
    ).prefetch_related(
        'activeloan__return_payments'
    )
    for loan in borrowed_loans:
        loan.percentage = round((loan.activeloan.total_paid / (loan.amount + loan.interest_amount)) * 100 , 2)
        if loan.payment_plan == "weekly":

            loan.schedule = get_installment_schedule(loan)
    
    lender = borrowed_loans[0].lender
    count = borrowed_loans.count()
    
    return render(request,'borrower/loan_details.html',{'count':count,'loans':borrowed_loans , "lender":lender , 'mini':1,'maxi':1000})
