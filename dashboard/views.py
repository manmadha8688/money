from django.shortcuts import render
from loans.models import LoanRequest
from django.db.models import Sum
from django.db.models import Prefetch
from active_loans.models import ActiveLoan,ReturnPayment
from collections import defaultdict
from datetime import date, timedelta

from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.utils.timezone import now


def interest_earned(loan):
    if not hasattr(loan, 'activeloan'):
        return Decimal('0.00')
    
    active = loan.activeloan
    repayments = active.return_payments.all()
    
    total_paid = repayments.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_loan_amount = Decimal(loan.amount) + Decimal(loan.interest_amount)
    
    # Calculate proportional interest earned
    paid_ratio = total_paid / total_loan_amount if total_loan_amount > 0 else 0
    earned_interest = Decimal(loan.interest_amount) * paid_ratio
    
    return earned_interest.quantize(Decimal('0.01'))

def earned_interest_monthly(loan):
    if not hasattr(loan, 'activeloan') or loan.payment_plan != 'monthly':
        return Decimal('0.00')

    active = loan.activeloan
    repayments = active.return_payments.all()

    if not loan.taken_date or not repayments.exists():
        return Decimal('0.00')

    interest = loan.interest_amount or Decimal('0.00')
    earned = Decimal('0.00')

    # Start from taken date
    period_start = loan.taken_date
    today = date.today()

    while period_start < today:
        period_end = period_start + relativedelta(months=+1)

        # Check if there is any payment between this period
        has_payment = repayments.filter(
            created_at__date__gte=period_start,
            created_at__date__lt=period_end
        ).exists()

        if has_payment:
            earned += interest
            period_start = period_end
        else:
            break  # stop at first unpaid month

    return earned.quantize(Decimal('0.01'))

def get_trend_data(current, previous):
    if previous == 0:
        return {'change': 100 if current > 0 else 0, 'direction': 'up' if current > 0 else 'neutral'}
    diff = current - previous
    percent = abs((diff / previous) * 100)
    return {
        'change': round(percent, 2),
        'direction': 'up' if diff > 0 else 'down'
    }

def calculate_overdue_by_custom_weeks(due_date, today, installment):
    first_overdue_day = due_date + timedelta(days=1)
    if today < first_overdue_day:
        return 0
    days_passed = (today - first_overdue_day).days
    weeks_passed = days_passed // 7 + 1  # include the first overdue installment
    return weeks_passed * installment

def calculate_monthly_overdue(due_date, today, monthly_installment):
    first_overdue_day = due_date + timedelta(days=1)
    if today < first_overdue_day:
        return 0
    
    months_passed = 0
    check_date = first_overdue_day

    # Count how many full months passed (each interval is 1 month from first overdue)
    while check_date <= today:
        months_passed += 1
        check_date += relativedelta(months=1)
    
    return months_passed * monthly_installment
    
def calculate_daily_overdue(due_date, today, daily_installment):
    first_overdue_day = due_date + timedelta(days=1)
    if today < first_overdue_day:
        return 0
    overdue_days = (today - first_overdue_day).days + 1  # include today
    return overdue_days * daily_installment

@login_required
def dashboard(request):
    
    active_loans_qs = LoanRequest.objects.filter(
        status='paymentreceived'
    ).select_related(
        'payment',       # OneToOneField → fast JOIN
        'activeloan',
        'borrower'    # OneToOneField → fast JOIN
    ).prefetch_related(
        Prefetch(
            'activeloan__return_payments',
            queryset=ReturnPayment.objects.filter(status='success')
        )
    )

# Step 2: Get borrowers (clients) of the lender and attach only their active loans
    borrowers = request.user.lender_clients.prefetch_related(
        Prefetch('client_loans', queryset=active_loans_qs, to_attr='active_loans')
    )

    total_borrowers = len(borrowers)

    total_collected ,total_pending , total_lent , total_overdue = 0 ,0,0,0

    today = date.today()
    start_current = today - timedelta(days=30)
    start_previous = start_current - timedelta(days=30)
    end_previous = start_current



    current_month = today.month
    current_year = today.year
    last_month = current_month - 1 if current_month > 1 else 12
    last_month_year = current_year if current_month > 1 else current_year - 1


    last_month_loans = 0
    last_month_amount = 0
    last_month_overdue_amount = 0
    last_month_overdue_loans = 0
    total_interest_earned = Decimal('0.00')

# Initialize counters
    this_month_loans = 0
    this_month_amount = 0
    tomorrow = today + timedelta(days=1)
    today_payable = 0
    tomorrow_payable = 0
    today_payable_planwise = defaultdict(int)
    today_payable_planwise['total'] = 0
    tomorrow_payable_planwise = defaultdict(int)
    tomorrow_payable_planwise['total'] = 0
    loans_planwise = defaultdict(int)
    total_amount_planwise =  defaultdict(int)
    total_amount_collected_planwise = defaultdict(int)

    total_loans = 0
    
    closed_loans,ongoing_loans,overdue_loans = 0,0,0
    today_loans = []
    tomorrow_loans = []
    overdue_members = []
    for borrower in borrowers:
        borrower.status = "Good"
        borrower.total_lent = 0
        borrower.total_paid = 0
        borrower.loans = 0
        for loan in borrower.active_loans:
            borrower.loans += 1
            borrower.total_lent += loan.amount
            total_lent += loan.amount
            total_loans += 1
            loans_planwise[loan.payment_plan] += 1
            total_amount_planwise[loan.payment_plan] += loan.amount
            if loan.taken_date and loan.taken_date.month == current_month and loan.taken_date.year == current_year:
                this_month_loans += 1
                this_month_amount += loan.amount
            elif loan.taken_date.month == last_month and loan.taken_date.year == last_month_year:
                last_month_loans += 1
                last_month_amount += loan.amount
            if loan.payment_plan == "monthly":
                total_interest_earned += earned_interest_monthly(loan)
            else :
                total_interest_earned += interest_earned(loan)


            if hasattr(loan, 'activeloan'):
                active = loan.activeloan
                total_collected += active.total_paid
                borrower.total_paid += active.total_paid
                

                if active.status == 'overdue':
                    borrower.status = 'overdue'
                    if loan.payment_plan == "weekly":
                        overdue_amount = calculate_overdue_by_custom_weeks(active.next_due_date, today, loan.instalment)
                    elif loan.payment_plan == "monthly":
                        overdue_amount = calculate_monthly_overdue(active.next_due_date, today, loan.instalment)
                    else:
                        overdue_amount = calculate_daily_overdue(active.next_due_date, today, loan.instalment)
                    total_overdue += overdue_amount
                    overdue_loans += 1

                    overdue_members.append({
                        'borrower': loan.borrower,
                        'loan': loan,
                        'due_date': active.next_due_date,
                        'amount': overdue_amount,
                        })

                    
                    if active.next_due_date.month == last_month and active.next_due_date.year == last_month_year:
                        if loan.payment_plan == "monthly":

                            last_month_overdue_amount += loan.instalment
                        elif loan.payment_plan=="weekly":
                            last_month_overdue_amount += calculate_overdue_by_custom_weeks(active.next_due_date, today.replace(day=1), loan.instalment)
                        else:
                            last_month_overdue_amount += calculate_daily_overdue(active.next_due_date, today.replace(day=1), loan.instalment)
                        last_month_overdue_loans += 1
                elif active.status == "closed":
                    closed_loans += 1
                else :
                    ongoing_loans += 1 


                if active.next_due_date == today:
                    today_payable += loan.instalment or 0
                    today_payable_planwise[loan.payment_plan] += loan.instalment or 0
                    today_payable_planwise['total'] += loan.instalment
                    today_loans.append({'loan': loan, 'due':'Today'})

                elif active.next_due_date == tomorrow:
                    tomorrow_payable += loan.instalment or 0
                    tomorrow_payable_planwise[loan.payment_plan] += loan.instalment or 0
                    tomorrow_payable_planwise['total'] += loan.instalment or 0
                    tomorrow_loans.append({'loan': loan, 'due':'Tomorrow'})
           
                

                for payment in active.return_payments.all():
                    total_amount_collected_planwise[loan.payment_plan] += payment.amount
                    payment_date = payment.created_at.date()

        
    total_pending = max(total_lent - total_collected,0)
    loans_at_risk = today_loans + tomorrow_loans
    avg_loan_amount = round(total_lent / total_loans) if total_loans > 0 else 0

    context = {
        'borrowers':borrowers,
        'total_lent':total_lent,
        'total_collected':total_collected,
        'total_pending':total_pending,
        'total_overdue':total_overdue,
        'today_payable':today_payable,
        'tomorrow_payable':tomorrow_payable,
        'today_payable_planwise': dict(today_payable_planwise),
        'tomorrow_payable_planwise': dict(tomorrow_payable_planwise),
        'total_borrowers' : total_borrowers,
        'total_loans':total_loans,
        'total_amount_planwise' : total_amount_planwise,
        'total_amount_collected_planwise' : total_amount_collected_planwise,
        'loans_planwise': dict(loans_planwise),
        'closed_loans' : closed_loans,
        'ongoing_loans' : ongoing_loans,
        'overdue_loans' : overdue_loans,
        'avg_loan_amount' : avg_loan_amount,
        'this_month_loans': this_month_loans,
        'this_month_amount': this_month_amount,
        'last_month_loans': last_month_loans,
        'last_month_amount': last_month_amount,
        'last_month_overdue_amount':last_month_overdue_amount,
        'last_month_overdue_loans' : last_month_overdue_loans,
        'total_interest_earned' : total_interest_earned,

        
        'loans_at_risk' : loans_at_risk,

        'overdue_members':overdue_members


    }
    return render(request,'dashboard.html',context)
def new_loan(request):
    return render(request,'lender/new_loan.html')
