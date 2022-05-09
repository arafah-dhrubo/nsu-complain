from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.auth import logout, update_session_auth_hash, authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, AdminPasswordChangeForm
from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage, send_mail
from social_django.models import UserSocialAuth
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from accounts.models import Profile
from accounts.tokens import account_activation_token


def login_account(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        # Checking if user is valid
        print(user)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login Successful')
            return redirect('/')

        else:
            messages.error(request, 'Invalid Username or Password')
            return redirect('login')
    else:
        if request.user.is_authenticated:
            return redirect('/')
        else:
            return render(request, 'auth/login.html')


def logout_account(request):
    if not request.user.password:
        messages.error(request, 'Change password first')
        return redirect('/')

    if request.user.is_authenticated:
        logout(request)
        return redirect('/')


def register(request):
    if request.method == 'POST' and request.FILES:
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password']
        password2 = request.POST['password2']
        photo = request.FILES['photo']

        if password1 == password2:
            # Checking unique email
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email address already used')
                return redirect('/')

            # Checking unique username
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already used')
                return redirect('/')

            # Create new username
            user = User.objects.create_user(username=username, email=email, password=password1)
            user.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            # Save ID Card Photo in Profile Model
            profile = Profile.objects.create(user=request.user, photo=photo)
            profile.save()
            # Sending accounts verification mail
            verify_account(request)
            return redirect('/')
        else:
            messages.info(request, 'Password not matching')
            return redirect('signup')
    else:
        if request.user.is_authenticated:
            return redirect('/')
        else:
            return render(request, 'auth/register.html')


def verify_account(request):
    user = request.user
    current_site = get_current_site(request)
    mail_subject = 'Activate your account.'
    message = render_to_string('mail_templates/mail_template.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
    })
    to_email = user.email
    email = EmailMessage(
        mail_subject, message, to=[to_email]
    )
    email.content_subtype = 'html'
    email.send()
    messages.success(request, 'Verification email has been sent')
    return redirect('/')


def activate(request, uidb64, token):
    if request.user.profile.is_verified:
        messages.error(request, 'Already verified')
        return redirect('/')
    else:
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.profile.is_verified = True
            user.profile.save()
            messages.success(request, 'Account verified successfully')
            return redirect('/')
        else:
            messages.error(request, 'verification link is invalid')
            return redirect('/')



@login_required
def settings(request):
    user = request.user
    if not user.social_auth.count():
        return redirect('/')
    else:
        try:
            github_login = user.social_auth.get(provider='github')
        except UserSocialAuth.DoesNotExist:
            github_login = None

        try:
            google_login = user.social_auth.get(provider='google-oauth2')
        except UserSocialAuth.DoesNotExist:
            google_login = None

        can_disconnect = (user.social_auth.count() > 1 or user.has_usable_password())

        return render(request, 'auth/settings.html', {
            'github_login': github_login,
            'google_login': google_login,

            'can_disconnect': can_disconnect
        })


@login_required
def password(request):
    if request.user.has_usable_password():
        PasswordForm = PasswordChangeForm
    else:
        PasswordForm = AdminPasswordChangeForm

    if request.method == 'POST':
        form = PasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordForm(request.user)
    return render(request, 'auth/password.html', {'form': form})
