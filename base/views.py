from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import render, redirect

from accounts.models import Profile
from base.models import Complain


@login_required
def home(request):
    data = Complain.objects.filter(user_id=request.user.id).order_by('-date_created')
    return render(request, 'base/home.html', {'data': data})


@login_required
def send_complain(request):
    is_exists = Profile.objects.filter(user=request.user).first()
    if is_exists:
        if not is_exists.is_verified:
            messages.warning(request, 'Verify account first')
            return redirect('/')
    subject = "complain"
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        raw_message = request.POST['message']
        Complain.objects.create(user=request.user, phone=phone, mail=email, message=raw_message)
        message = f'Hi {name}, I am {request.user.username} \n\n{raw_message} \n\nPlease Contact me {phone}'
        email_from = request.user.email
        recipient_list = [email, ]
        send_mail(subject, message, email_from, recipient_list)
        messages.success(request, 'Mail has been sent')
        return redirect('/')
    return render(request, 'base/send_complain.html')


@login_required
def all_complains(request):
    data = Complain.objects.filter(user_id=request.user.id).order_by('-date_created')
    return render(request, 'base/all_complains.html', {'data': data})


@login_required
def single_complain(request, cid):
    data = Complain.objects.get(id=cid)
    if data.user != request.user:
        messages.warning(request, 'Unauthorized email checking')
        return redirect('/')
    return render(request, 'base/complain.html', {'data': data})
