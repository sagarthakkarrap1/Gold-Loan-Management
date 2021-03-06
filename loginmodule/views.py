from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.template.context_processors import csrf
from django.contrib import messages
from applyforloan.models import Customer, GoldAsset, LoanApplication, LoanRates,Payment
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import requires_csrf_token
import string

def home(request):
    rate = LoanRates.objects.last()
    if rate is None:
                loanrate = LoanRates()
                loanrate.save()
                rate = LoanRates.objects.last()
    return render(request,"home.html",{"goldvalue":rate.GoldValue,"interest":rate.RateOfInterest,"ltv":rate.ltvRatio})

def login(request):
        c = {}
        c.update(csrf(request))
        return render(request,'login.html', c)

def auth_view(request):
    if request.method == "POST":
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username,password=password)
        if user is not None:
            auth.login(request, user)
            if user.is_superuser:
                return HttpResponseRedirect('/loginmodule/loggedin_admin/')
            else:
                return HttpResponseRedirect('/loginmodule/loggedin_customer/')
        else:
            messages.success(request,"Invalid credentials OR Loan Application has been rejected!! ")
    
    return redirect('/loginmodule/login')

@login_required(login_url='/loginmodule/login')
def loggedin_customer(request):
    c = Customer.objects.get(username = request.user.get_username())
    asset = GoldAsset.objects.get(customerId_id = c.customerId)
    application = LoanApplication.objects.get(customerId_id = c.customerId)
    payment = Payment.objects.get(customerId_id = c.customerId)
    month = application.emipaid + 1
    totalmonth = application.lentLoanTenure*12
    return render(request,'view_details.html', {"c":c,"a":asset,"appl":application,"p":payment,"month":month,"totalmonth":totalmonth})

@login_required(login_url='/loginmodule/login')
def loggedin_admin(request):
    c = Customer.objects.all()
    asset = GoldAsset.objects.all()
    application = LoanApplication.objects.all()
    rate = LoanRates.objects.last()
    context =  {"customer":c,"asset":asset,"application":application,"goldvalue":rate.GoldValue,
    "interest":rate.RateOfInterest,"ltv":rate.ltvRatio}
    return render(request,'admin.html',context) 

@login_required(login_url='/loginmodule/login')
def update_rates(request):
    if request.method == "POST":
        goldvalue = request.POST.get('goldvalue')
        interest = request.POST.get('interest')
        ltv_ratio = request.POST.get('ltv_ratio')
        rate=LoanRates(GoldValue=goldvalue,RateOfInterest=interest,ltvRatio=ltv_ratio)
        rate.save()
        return HttpResponseRedirect('/loginmodule/loggedin_admin/')
    else:
        return redirect('/loginmodule/login')

def logout(request):
    auth.logout(request)
    messages.info(request,"Logged out successfully..")
    return render(request,'login.html')

@login_required(login_url='/loginmodule/login')
def approve(request):
    if request.method == "POST":
        customerId = request.POST.get('customerId')
        l = LoanApplication.objects.get(customerId = customerId)
        l.loanApplicationStatus = "APP"
        l.save()
        return HttpResponseRedirect('/loginmodule/loggedin_admin/')
    else:
        return redirect('/loginmodule/login')

@login_required(login_url='/loginmodule/login')
def reject(request):
    if request.method == "POST":
        customerId = request.POST.get('customerId')
        l = LoanApplication.objects.get(customerId = customerId)
        g = GoldAsset.objects.get(customerId = customerId)
        p = Payment.objects.get(customerId = customerId)
        c = Customer.objects.get(customerId = customerId)
        username = c.username
        password = c.password
        user = auth.authenticate(username=username,password=password)
        user.delete()
        l.delete()
        g.delete()
        p.delete()
        c.delete()
        return HttpResponseRedirect('/loginmodule/loggedin_admin/')
    else:
        return redirect('/loginmodule/login')

@login_required(login_url='/loginmodule/login')
def pay_emi(request):
    if request.method == "POST":
        customerId = request.POST.get('customerId')
        month = int(request.POST.get('month'))
        l = LoanApplication.objects.get(customerId = customerId)
        if month == l.lentLoanTenure*12:
            l.emipaid = month
            l.paid = l.emi + l.paid
            l.save()
            messages.success(request,"Congratulations,Full Loan Payment done!!")
        elif month < l.lentLoanTenure*12:
            l.emipaid = month
            l.paid = l.emi + l.paid
            l.save()
            payment_done="Payment done successfully for month = " + str(month)
            messages.success(request,payment_done)
        return redirect('/loginmodule/loggedin_customer/')
    else:
        return redirect('/loginmodule/login')
        
    

