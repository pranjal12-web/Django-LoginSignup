from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
from loginSignup import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import authenticate, login, logout
from . tokens import generate_token


# Create your views here.
#home function which is called when homepage url is requested
def home(request):
    #return HttpResponse("hello,I am working") #hello i am working is displayed on the requested url.
    return render(request,"authentication/index.html")

def signup(request):
    #when the form is submitted store all the entered data into these variables.
    if request.method == "POST":
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

         
        if User.objects.filter(username=username):
            messages.error(request, "Username already exist! Please try some other username.")
            return redirect('home')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email Already Registered!!")
            return redirect('home')
        
        if len(username)>20:
            messages.error(request, "Username must be under 20 charcters!!")
            return redirect('home')
        
        if pass1 != pass2:
            messages.error(request, "Passwords didn't matched!!")
            return redirect('home')
        
        if not username.isalnum():
            messages.error(request, "Username must be Alpha-Numeric!!")
            return redirect('home')

        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active=False #initially let us keep the user inactive . only when the user clicks the activation link the username will become active

         #save the created user
        myuser.save()
        messages.success(request, "Your Account has been created succesfully!! Please check your email to confirm your email address in order to activate your account.")

     
        from_email = settings.EMAIL_HOST_USER #emailid of the person sending the email
        to_list = [myuser.email] #emailid to which email is sent i.e user emailid
      

        # Email Address Confirmation Email
        current_site = get_current_site(request)
        email_subject = "Confirm your Email!!"
        message2 = render_to_string('email_confirmation.html',{
            
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser)
        })

        send_mail(email_subject, message2, from_email, to_list, fail_silently=True)
       
        
    
#redirecting to signin page
        return redirect('signin')
    return render(request,"authentication/signup.html")

def signin(request):
     if request.method == "POST":
        username = request.POST['username']
        pass1 = request.POST['pass1']

        user=authenticate(username=username,password=pass1) 
        #authenticate whether the user exists or not by matching the username and password.

        if user is not None:
            login(request,user)
            fname=user.first_name
            return render(request,"authentication/index.html",{'fname':fname})
        else:
            messages.error(request,"Bad credentials")
            return redirect('home')

        
     return render(request,"authentication/signin.html")

def signout(request):
    logout(request)
    messages.success(request,"logout successful!")
    return redirect('home')
    

def activate(request,uidb64,token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active = True
        # user.profile.signup_confirmation = True
        myuser.save()
        login(request,myuser)
        messages.success(request, "Your Account has been activated!!")
        return redirect('signin')
    else:
        return render(request,'activation_failed.html')