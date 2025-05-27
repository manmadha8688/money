from django.shortcuts import render

# Create your views here.
def dashboard(request):
    return render(request,'dashboard.html')
def new_loan(request):
    return render(request,'lender/new_loan.html')
