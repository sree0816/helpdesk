from django.shortcuts import render,redirect
from agents.models import Agent

# Create your views here.
def adminhome(request):
    return render(request,'homeadmin.html')
def dashboard(request):
    return render(request,'dashboard.html')
def register(request):
    return render(request,'register.html')
def save_agent(request):
    if request.method=='POST':
        a=request.POST.get('name')
        b=request.POST.get('email')
        c=request.POST.get('password')
        obj=Agent(name=a,email=b,password=c,is_available='False')
        obj.save()
    return redirect(adminhome)



