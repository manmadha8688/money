from django.shortcuts import render, get_object_or_404,redirect
from django.contrib.auth.models import User
from .models import LoanRequest, Borrower , PaymentDetail ,LoanStatusHistory ,LoanImage
from datetime import date
from django.http import JsonResponse
from django.utils.timezone import now
from django.shortcuts import get_object_or_404, render
from django.utils.timezone import now
from datetime import datetime
from .models import LoanRequest, Borrower, User
from django.db.models import Q

def draft_loan(request, lender_id, unique_id):
    if request.method == 'POST':
        print(lender_id)
        lender = get_object_or_404(User, id=lender_id)

        loan = LoanRequest.objects.filter(lender=lender, unique_id=unique_id).first()
        if loan is None:
            loan = LoanRequest.objects.create(
                lender=lender,
                unique_id=unique_id,
                submitted=False,
                amount=0,
                apply_date=now()
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
def loan_request(request, lender_id, unique_id):
    lender = get_object_or_404(User, id=lender_id)
    
    loan = LoanRequest.objects.get(lender=lender, unique_id=unique_id)

    if loan is None:
        return JsonResponse({'error': 'Loan form not found'}, status=404)

    if loan and loan.submitted:
        if loan.status == "pending":
            if request.method == 'POST':
                if request.POST.get('edit') == 'edit':
                    loan.submitted = False
                    loan.save()
                    lender_id = loan.lender.id
                    unique_id = loan.unique_id

                    return redirect('new-loan', lender_id=lender_id, unique_id=unique_id)
            return render(request, "borrower/loan_already_submitted.html", {"loan": loan})
        elif loan.status == "accepted":
            return render(request, "borrower/loan_confirmation.html", {"loan": loan})
        elif loan.status== "rejected":
            return render(request, "borrower/loan_rejected.html", {"loan": loan})
        elif loan.status== "cancelled":
            return render(request, "borrower/loan_cancelled.html", {"loan": loan})
        elif loan.status== "paymentprocess":
            payment = PaymentDetail.objects.get(id =loan.payment.id)
            return render(request, "borrower/payment_process.html", {"loan": loan,"payment":payment})
        else :
            
            payment = PaymentDetail.objects.get(id =loan.payment.id)
            return render(request, "borrower/payment_confirmation.html", {"loan": loan,"payment":payment})
        


    if request.method == "POST":
        borrower_name = request.POST["borrower_name"]
        phone = request.POST.get("phone", "")
        email = request.POST.get("email", "")

        # Get or create borrower
        borrower, _ = Borrower.objects.get_or_create(name=borrower_name, phone=phone, email=email)

        # Convert date fields safely
        taken_date = datetime.strptime(request.POST["taken_date"], "%Y-%m-%d").date()
        return_date = datetime.strptime(request.POST["return_date"], "%Y-%m-%d").date()

        # Save loan details
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


        loan.save()

        return render(request, "borrower/loan_already_submitted.html", {"loan": loan})
    

    return render(request, "borrower/loan_request_form.html", {"loan": loan})

def loan_request_list(request):
    loan_requests = LoanRequest.objects.filter(lender=request.user, submitted=True,status="pending")
    return render(request,'lender/loan_requested_list.html',{"loan_requests":loan_requests})

def accept_reject_status(request, loan_id):
    if request.method == "POST":
        loan = get_object_or_404(LoanRequest, id=loan_id)
        loan.interest = request.POST.get("interest")
        loan.amount = request.POST.get("amount")
        loan.taken_date = request.POST.get("taken_date")
        loan.return_date = request.POST.get("return_date")

        action = request.POST.get("action")
        if action == "accept":
            loan.status = "accepted"
        elif action == "reject":
            loan.status = "rejected"
        loan.remark = request.POST.get('remark')
        loan.save()

        return redirect("loan-request-list")  # your loan list page

def accepted_list(request):
    loans = LoanRequest.objects.filter(lender=request.user, submitted=True).filter(Q(status="accepted") | Q(status="paymentprocess"))
    
    return render(request,'lender/accepted_list.html',{"loans":loans}) 

def cancle_loan(request,loan_id):
    loan = get_object_or_404(LoanRequest, id=loan_id)
    loan.status = "cancelled"
    if request.method == 'POST':

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

            if online_method in ['phonepe', 'googlepay', 'paytm']:
                payment.upi_number = request.POST.get('upi_number')
                if 'upi_screenshot' in request.FILES:
                    payment.upi_screenshot = request.FILES['upi_screenshot']

            elif online_method == 'bank':
                payment.account_number = request.POST.get('account_number')
                payment.ifsc = request.POST.get('ifsc')
                payment.bank_name = request.POST.get('bank_name')
        payment.loan = loan
        payment.save()
        loan.payment = payment
        loan.status = 'paymentprocess'
        loan.save()
    

    

    return redirect('new-loan', lender_id=lender_id, unique_id=unique_id)
def cancel_reject_list(request):
    loans = LoanRequest.objects.filter(Q(status="rejected") | Q(status="cancelled")).order_by('-id')
    return render(request, 'lender/cancel_reject_list.html', {'loans': loans})

def paymentdone(request,loan_id):
    if request.method == "POST": 
        utr = request.POST.get('utr', '').strip()
        bank = request.POST.get('bank', '').strip()
        person = request.POST.get('person', '').strip()
 
        loan = LoanRequest.objects.get(id=loan_id)
        loan.payment.utr = utr
        loan.payment.bank = bank
        loan.payment.person = person
        
        loan.status="paymentdone"
        loan.remark = "✅ Payment is done — waiting for confirmation."
        loan.payment.save()
        loan.save()
        

    return redirect("accepted-list")

def paymentreceived(request,loan_id):
    loan = get_object_or_404(LoanRequest, id=loan_id)
    if request.method == "POST":
        confirmation = request.POST.get('confirmation')
        if confirmation == "yes":
            loan.status = "paymentreceived"
            loan.remark = "Payment is received and Confirmed by client "
            loan.save()
        else:
            loan.status = "paymentnotreceived"
            loan.remark = "Payment is not received by client. Please contact client"
            loan.save()
            
    
    lender_id = loan.lender.id
    unique_id = loan.unique_id

    return redirect('new-loan', lender_id=lender_id, unique_id=unique_id)
def payment_done_list(request):
    loans = LoanRequest.objects.filter(Q(status="paymentdone") | Q(status="paymentnotreceived"))
    
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
    loans = LoanRequest.objects.filter(submitted= True)
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
