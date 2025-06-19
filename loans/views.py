from django.shortcuts import render, get_object_or_404,redirect
from django.contrib.auth.models import User
from django.urls import reverse
from .models import LoanRequest, Borrower , PaymentDetail ,LoanStatusHistory ,LoanImage

from django.http import JsonResponse
from django.utils.timezone import now
from django.shortcuts import get_object_or_404, render
from datetime import datetime ,timedelta
from dateutil.relativedelta import relativedelta

from .models import LoanRequest, Borrower, User
from django.db.models import Q
from django.contrib import messages

from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa

from active_loans.models import ActiveLoan,ReturnPayment

def apply_filter(loans,request):

    borrower = request.GET.get('borrower', '').strip()
    token = request.GET.get('token', '').strip()
    status = request.GET.get('status', '').strip()
    mobile_number = request.GET.get('mobile_number', '').strip()
    
    if token:
        loans = loans.filter(id=token)
    if borrower:
        loans = loans.filter(borrower__name__icontains = borrower)
    if status :
        loans = loans.filter(status=status)
    if mobile_number :
        
        loans = loans.filter(borrower__phone__icontains = mobile_number)
    return loans
def draft_loan(request, lender_id, unique_id):
    if request.method == 'POST':
        
        lender = get_object_or_404(User, id=lender_id)

        loan = LoanRequest.objects.filter(lender=lender, unique_id=unique_id).first()
        if loan is None:
            loan = LoanRequest.objects.create(
                lender=lender,
                unique_id=unique_id,
                submitted=False,
                amount=0,
            )
            created = True
        else:
            created = False  # Already exists, no new draft created

        return JsonResponse({
            'message': 'Draft loan processed',
            'created': created,
            'loan_id': loan.id
        }) 

    return JsonResponse({'error': 'Invalid request method'}, status=400)



from django.db.models import Sum

def get_installment_schedule(loan):
    total_installments = 14
    start_date = loan.taken_date
    total_amount = loan.amount + loan.interest_amount
    
    # ActiveLoan info
    activeloan = loan.activeloan
    next_due_date = activeloan.next_due_date
    
    # Prefetched ReturnPayments related to this activeloan (assumed loan.prefetch_related('activeloan__return_payments'))
    repayments = activeloan.return_payments.all()
    
    schedule = []
    total_paid = 0
    remaining = total_amount

    for week in range(total_installments):
        due_date = start_date + timedelta(weeks=week + 1)
        
        # Sum all payments matching this due_date
        paid_this_due_date = 0
        payment_details =[]
        # If due_date is before next_due_date, consider it paid (or partially paid)
        status = due_date < next_due_date
        if status:
            due_payments = repayments.filter(due_date=due_date)
            paid_this_due_date = due_payments.aggregate(
                total_paid=Sum('amount')
            )['total_paid'] or 0

            total_paid += paid_this_due_date
            remaining = total_amount - total_paid

            # Collect individual payment records
            payment_details = list(due_payments.values(
                
                'payment_method',
                'utr',
                'payment_app',
                'cash_person',
                'created_at'
            ))

        schedule.append({
            'week': week + 1,
            'due_date': due_date,
            'status': status,
            'paid_this_due_date': paid_this_due_date,
            
            'total_paid': total_paid,
            'remaining': remaining,
            'payment_details': payment_details,
        })

    return schedule



def loan_request(request, lender_id, unique_id):
    lender = get_object_or_404(User, id=lender_id)
    
    loan = get_object_or_404(
        LoanRequest.objects.select_related(
        'lender__active_user',
        'borrower',
        'payment',
        'activeloan'  
    ).prefetch_related(
        'activeloan__return_payments'
    ),
        lender=lender,
        unique_id=unique_id
    )

    if loan and loan.submitted:
        if loan.status == "pending" or loan.status == "accepted":
            payment = loan.payment
            if request.method == 'POST':
                if request.POST.get('edit') == 'edit':
                    loan.submitted = False
                    loan.save()
                    lender_id = loan.lender.id
                    unique_id = loan.unique_id

                return redirect('new-loan', lender_id=lender_id, unique_id=unique_id)
            
            return render(request, "borrower/payment_process.html", {"loan": loan,"payment":payment})
        elif loan.status== "rejected":
            return render(request, "borrower/loan_rejected.html", {"loan": loan})
        elif loan.status== "cancelled":
            return render(request, "borrower/loan_cancelled.html", {"loan": loan})
        
        elif loan.status == "paymentdone" or loan.status == 'paymentnotreceived':
            
            payment = PaymentDetail.objects.get(id =loan.payment.id)
            return render(request, "borrower/payment_confirmation.html", {"loan": loan,"payment":payment})
        else :
            return render(request,'borrower/completed_loan.html',{"loan": loan})
        """ 
        elif loan.status == 'paymentreceived':
            username = 
            default_password = User.objects.make_random_password(length=8)  # You can also use a fixed one
    
   
            user = User.objects.create_user(
                username=username,
                password=default_password,
                email=email,
                first_name=name,
                last_name="True"  # Flag for password change
                )

    # Return the created user and password to inform admin or send via SMS/email
            return {
                    "username": username,
                    "temporary_password": default_password
                }
        else :
            
            if loan.payment_plan == "monthly":
                mini = loan.interest_amount
                maxi = loan.activeloan.remaining_balance
                payment_exists = False
                if request.method == "POST":

                    
                    amount = request.POST.get('amount')
                    payment_method = request.POST.get('method')
                    utr = request.POST.get('utr', '')
                    cash_person = request.POST.get('cash_person', '')
                    payment_app = request.POST.get('platform', '')
                    due_date = datetime.strptime(request.POST["due_date"], "%Y-%m-%d").date()
                    
                    existing_payment = ReturnPayment.objects.filter(
                        returnloan=loan.activeloan,
                        due_date=due_date, # optionally filter by pending only
                        ).first()
                    
                    if not existing_payment:
                        payment = ReturnPayment(
                            returnloan=loan.activeloan,
                            amount=amount,
                            payment_method=payment_method,
                            utr=utr,
                            cash_person=cash_person,
                            payment_app=payment_app,
                            due_date=due_date,
                        )
                        payment.save()
                        
                    else:
                        payment_exists = True


                return render(request, "borrower/loan_details.html",{"loan":loan, 'mini':mini,'maxi':maxi,"payment_exists":payment_exists})
            elif loan.payment_plan == "weekly":
                schedule = get_installment_schedule(loan)
                
                mini = loan.instalment
                maxi = loan.activeloan.remaining_balance
                if  maxi < mini :
                    mini = maxi
                
                payment_exists = False
                if request.method == "POST":

                    
                    amount = request.POST.get('amount')
                    
                    payment_method = request.POST.get('method')
                    utr = request.POST.get('utr', '')
                    cash_person = request.POST.get('cash_person', '')
                    payment_app = request.POST.get('platform', '')
                    due_date = datetime.strptime(request.POST["due_date"], "%Y-%m-%d").date()
                    
                    existing_payment = ReturnPayment.objects.filter(
                        returnloan=loan.activeloan,
                        due_date=due_date,  # optionally filter by pending only
                        ).first()

                    if not existing_payment:
                        payment = ReturnPayment(
                            returnloan=loan.activeloan,
                            amount=amount,
                            payment_method=payment_method,
                            utr=utr,
                            cash_person=cash_person,
                            payment_app=payment_app,
                            due_date=due_date,
                        )
                        payment.save()
                        
                    else:
                        payment_exists = True
                        request.session['payment_exists'] = True
                        return redirect('new-loan', lender_id=lender_id, unique_id=unique_id)


                payment_exists = request.session.pop('payment_exists', False)
                return render(request, "borrower/loan_details.html",{"loan":loan,'schedule': schedule, 'mini':mini,'maxi':maxi,"payment_exists":payment_exists})
            else :
                return render(request, "borrower/repaying_onetime_loan.html",{"loan":loan})
                
    """


    if request.method == "POST":
        
        name = request.POST.get("name")
        
        borrower_name = request.POST["borrower_name"]
        phone = request.POST.get("phone", "")
        email = request.POST.get("email", "")
        
        
        # Get or create borrower
        borrower, _ = Borrower.objects.get_or_create(name=borrower_name, phone=phone, email=email)

        # Convert date fields safely
        taken_date = datetime.strptime(request.POST["taken_date"], "%Y-%m-%d").date()
        return_date = datetime.strptime(request.POST["return_date"], "%Y-%m-%d").date()

        # Save loan details
        loan.payment_plan = request.POST.get("payment_plan", "")
        loan.borrower = borrower
        loan.loan_item = request.POST.get("loan_item", "")
        loan.amount = request.POST["amount"]
        loan.apply_date = now()
        loan.taken_date = taken_date
        loan.return_date = return_date
        loan.referral = request.POST.get("referral", "")
        loan.reason = request.POST.get("reason", "")
        loan.submitted = True

        photos = request.FILES.getlist('photos')

        for photo in photos:
           LoanImage.objects.create(loan=loan, image=photo)
        
            
        payment_type = request.POST.get('payment_type')

        payment = PaymentDetail(
            payment_method=payment_type
        )

        if payment_type == 'cash':
            cash_from = request.POST.get('cash_from')
            if cash_from:
                payment.cash_from = cash_from

        elif payment_type == 'online':
            online_method = request.POST.get('online_method')
            payment.online_method = online_method

            if online_method in ['phonepay', 'googlepay', 'paytm']:
                payment.upi_number = request.POST.get('upi_number')
                payment.account_holder = request.POST.get('account_holder_name').strip()
                if 'upi_screenshot' in request.FILES:
                    payment.upi_screenshot = request.FILES['upi_screenshot']

            elif online_method == 'bank':
                payment.account_number = request.POST.get('account_number')
                payment.ifsc = request.POST.get('ifsc')
                payment.bank_name = request.POST.get('bank_name')
                payment.account_holder = request.POST.get('bank_account_holder_name','').strip()
                
        payment.loan = loan
        payment.save()
        loan.payment = payment
        
        loan.save()

        return render(request, "borrower/payment_process.html", {"loan": loan})
    

    return render(request, "borrower/loan_request_form.html", {"loan": loan})
 
def loan_request_list(request):
    loan_requests = LoanRequest.objects.filter(lender=request.user, submitted=True,status__in = ["pending",'accepted']).select_related('borrower','payment')
    if request.method == "GET":
        loan_requests = apply_filter(loan_requests,request)
    return render(request,'lender/loan_requested_list.html',{"loan_requests":loan_requests})

from decimal import Decimal
def accept_reject_status(request, loan_id):
     
    loan = get_object_or_404(LoanRequest, id=loan_id)
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "accept":
            loan.status = "accepted"
            loan.interest = request.POST.get("interest")
            loan.amount = request.POST.get("amount")
            loan.taken_date = request.POST.get("taken_date")
            loan.interest_amount = Decimal(request.POST.get('interest_amount'))
            loan.instalment = request.POST.get('installment')
            loan.remark = request.POST.get('remark')
            loan.save()
            return redirect(f"{reverse('loan-request-list')}?accept=true&loan_id={loan.id}&amount={loan.amount}")
        elif action == "reject":
            loan.status = "rejected"
            loan.remark = request.POST.get('remark')
            loan.save()
            return redirect(f"{reverse('loan-request-list')}?reject=true&loan_id={loan.id}&amount={loan.amount}")
        

        return redirect("loan-request-list")  # your loan list page

def accepted_list(request):
    loans = LoanRequest.objects.filter(
    lender=request.user,
    submitted=True
    ).filter(
    Q(status="accepted") | Q(status="paymentprocess")
    ).select_related('payment','borrower').order_by('-updated_at')
    if request.method == "GET":
        loans = apply_filter(loans,request)
    return render(request,'lender/accepted_list.html',{"loans":loans}) 

def cancle_loan(request,loan_id):
    loan = get_object_or_404(LoanRequest, id=loan_id)
    if loan.status not in ['pending','accepted']:
        messages.error(request,"The loan is confirmed and can no longer be canceled. Let us know if you need help or have any questions!")
    elif request.method == 'POST':
        loan.status = "cancelled"
        loan.remark = request.POST.get('remark')
        loan.save()
    lender_id = loan.lender.id
    unique_id = loan.unique_id

    return redirect('new-loan', lender_id=lender_id, unique_id=unique_id)

def reject_loan(request,loan_id):
    loan = get_object_or_404(LoanRequest, id=loan_id)
    loan.status = "rejected"
    if request.method == 'POST':
        reamrk = request.POST.get('remark')
        loan.remark = reamrk
    loan.save()

    return redirect('accepted-list')

def payment_details(request, loan_id):
    loan = get_object_or_404(LoanRequest, id=loan_id)
    lender_id = loan.lender.id
    unique_id = loan.unique_id
    
    if request.method == 'POST':
        if loan.payment:
            
            return redirect('new-loan', lender_id=lender_id, unique_id=unique_id)
        if request.POST.get('instalment'):
            loan.instalment = request.POST.get('instalment')
            
        payment_type = request.POST.get('payment_type')

        payment = PaymentDetail(
            payment_method=payment_type
        )

        if payment_type == 'cash':
            cash_from = request.POST.get('cash_from')
            if cash_from:
                payment.cash_from = cash_from

        elif payment_type == 'online':
            online_method = request.POST.get('online_method')
            payment.online_method = online_method

            if online_method in ['phonepay', 'googlepay', 'paytm']:
                payment.upi_number = request.POST.get('upi_number')
                payment.account_holder = request.POST.get('account_holder_name').strip()
                if 'upi_screenshot' in request.FILES:
                    payment.upi_screenshot = request.FILES['upi_screenshot']

            elif online_method == 'bank':
                payment.account_number = request.POST.get('account_number')
                payment.ifsc = request.POST.get('ifsc')
                payment.bank_name = request.POST.get('bank_name')
                payment.account_holder = request.POST.get('bank_account_holder_name','').strip()
                
        payment.loan = loan
        payment.save()
        loan.payment = payment
        loan.status = 'paymentprocess'
        loan.save()
    
    return redirect('new-loan', lender_id=lender_id, unique_id=unique_id)
def cancel_reject_list(request):
    loans = LoanRequest.objects.filter(lender=request.user ).filter(Q(status="rejected") | Q(status="cancelled")).select_related('lender__active_user').order_by('-updated_at')
    if request.method == 'GET':
        loans = apply_filter(loans,request)
    return render(request, 'lender/cancel_reject_list.html', {'loans': loans})

def paymentdone(request,loan_id):
    if request.method == "POST": 
        utr = request.POST.get('utr', '').strip()
        bank = request.POST.get('bank', '').strip()
        person = request.POST.get('person', '').strip()
        loan = LoanRequest.objects.get(id=loan_id)
        if utr or bank or person :
            loan.payment.utr = utr
            loan.payment.bank = bank
            loan.payment.person = person
        else:
            return JsonResponse({
            'message': 'Not a Valid payment',
            'loan_id': loan.id
            }) 
        
        loan.status="paymentdone"
        loan.payment.save()
        loan.save()
        return redirect(f"{reverse('loan-request-list')}?paymentdone=true&loan_id={loan.id}&amount={loan.amount}")

    return redirect("accepted-list")
def payment_done_check(request,loan_id):
    loan = get_object_or_404(LoanRequest,id=loan_id)
    loan.status = "paymentdone"
    loan.save()
    return redirect("payment-done-list")
def paymentreceived(request,loan_id):
    loan = get_object_or_404(LoanRequest.objects.select_related('lender__active_user','borrower'), id=loan_id)
    if request.method == "POST":
        
        confirmation = request.POST.get('confirmation')
        if confirmation == "yes":
            start_date = loan.taken_date
            if loan.payment_plan == "weekly":
                due_date = start_date + timedelta(days=7)
            elif loan.payment_plan == "monthly":
                due_date = start_date + relativedelta(months=+1)
            elif loan.payment_plan == "onetime":
                due_date =  start_date + timedelta(days=1)


            loan.status = "paymentreceived"
            loan.save()
            ActiveLoan.objects.create(
                loan_request = loan,
                remaining_balance = loan.amount + loan.interest_amount,
                next_due_date = due_date
            )
            username = loan.borrower.phone
            default_password = "client@123" # You can also use a fixed one
    
            # Create user
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                username=username,
                password=default_password,
                first_name=loan.borrower.name,
                last_name="true"  # You are using this as a flag
                )
            else:
                return redirect('client-login')
            return render(request,'borrower/client_inform.html',{"password":default_password})
    
    

        else:
            loan.status = "paymentnotreceived"
            loan.save()
            
    
    lender_id = loan.lender.id
    unique_id = loan.unique_id

    return redirect('new-loan', lender_id=lender_id, unique_id=unique_id)
def payment_done_list(request):
    loans = LoanRequest.objects.filter(lender=request.user ).filter(Q(status="paymentdone") | Q(status="paymentnotreceived")).select_related('payment','borrower').order_by('-updated_at')
    
    if request.method == "GET":
        loans = apply_filter(loans,request)
    status_dict = {}

    for loan in loans:
      for history in loan.status_history.all():
          if history.status == 'paymentdone':
              status_dict[loan.id] = history.updated_at

    context = {
    'loans': loans,
    'status': status_dict
    }
    return render(request, 'lender/payment_done_list.html', context)


def loan_status_records(request):
    loans = LoanRequest.objects.filter(lender=request.user , submitted= True).prefetch_related('status_history').order_by('id')
    if request.method == "GET":
        loans = apply_filter(loans,request)
    loans_with_status = []

    for loan in loans:
        # Create a dictionary for each status
        status_dates = {
            'accepted': '',
            'paymentprocess': '',
            'paymentdone': '',
            'paymentreceived': '',
            'paymentnotreceived': '',
            'rejected': '',
            'cancelled': ''
        }

        for history in loan.status_history.all():
            if history.status in status_dates:
                status_dates[history.status] = history.updated_at

        loans_with_status.append({
            'loan': loan,
            'status_dates': status_dates
        })
        
    return render(request, 'loan_status_records.html',{'loans_with_status': loans_with_status})

def delete_loan_item_image(request,image_id):
    image = get_object_or_404(LoanImage, id=image_id)
    loan_id = image.loan.id  # To redirect back to the loan detail/edit page
    
    image.delete()
    loan = get_object_or_404(LoanRequest,id=loan_id)
    lender_id = loan.lender.id
    unique_id = loan.unique_id

    return redirect('new-loan', lender_id=lender_id, unique_id=unique_id)



def generate_pdf(request,loan_id):
    agreement_date = now().strftime('%d-%m-%Y')   # ✅ Correct usage
    loan = get_object_or_404(LoanRequest,id=loan_id)
    context = {
        'agreement_date': agreement_date,
        'lender_name': loan.lender.active_user.company_name,
        'borrower_name': loan.borrower.name,
        'loan_amount': loan.amount,
        'interest_amount': loan.interest_amount,
        'loan_start_date': loan.taken_date,
        'loan_end_date': loan.return_date,
    }

    template = get_template("lender/terms_conditions.html")
    html = template.render(context)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "inline; filename=loan_agreement.pdf"

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)

    return response
