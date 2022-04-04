from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.core import signing
from .hashes import PBKDF2WrappedSHA1PasswordHasher

from .models import UserData, Privacy


def profile_view(request, username):
    try:
        userdata = UserData.objects.get(username=username)
    except Exception:
        # invlaid user url #
        url = reverse("login:error")
        return HttpResponseRedirect(url)

    try:
        # check user logged in
        current_username = signing.loads(request.session["user_key"])
        if current_username != username:
            raise Exception()
    except Exception:

        context = {
            "page_name": username,
            "session_valid": False,
            "username": username,
            "FirstName": userdata.firstname,
            "LastName": userdata.lastname,
            "Email": userdata.email,
        }
        return render(request, "login/profile.html", context)

    context = {
        "page_name": username,
        "session_valid": True,
        "username": username,
        "FirstName": userdata.firstname,
        "LastName": userdata.lastname,
        "Email": userdata.email,
    }
    # valid username
    return render(request, "login/profile.html", context)


def user_profile(request, username, page):
    try:
        # check valid username
        userdata = UserData.objects.get(username=username)
    except:
        # not a valid username
        url = reverse("login:error")
        return HttpResponseRedirect(url)

    # valid username
    try:
        # check user logged in
        current_username = signing.loads(request.session["user_key"])
        if current_username != username:
            raise Exception()
    except Exception:
        # user not logged in
        url = reverse("login:profile", kwargs={"username": username})
        return HttpResponseRedirect(url)

    # user logged in
    context = {
        "page_name": username,
        "session_valid": True,
        "username": current_username,
        "profile_username": username,
    }
    # user is logged in & user is looking for his own profile #
    return render(request, "login/user_profile.html", context)


def user_privacy(request, username, page):
    try:
        current_username = signing.loads(request.session["user_key"])
        if current_username != username:
            raise Exception()
    except Exception:
        url = reverse("login:error")
        return HttpResponseRedirect(url)

    context = {
        "page_name": username,
        "session_valid": True,
        "username": current_username,
    }

    return render(request, "login/user_privacy.html", context)


def user_change_password(request, username, page):
    try:
        current_username = signing.loads(request.session["user_key"])
        if current_username != username:
            raise Exception()
    except Exception:
        url = reverse("login:error")
        return HttpResponseRedirect(url)

    context = {
        "page_name": username,
        "session_valid": True,
        "username": current_username,
    }

    return render(request, "login/user_password.html", context)


def settings(request, username, page):
    if "profile" in page:
        return user_profile(request, username, page)
    elif "privacy" in page:
        return user_privacy(request, username, page)
    elif "password" in page:
        return user_change_password(request, username, page)
    else:
        url = reverse("login:error")
        return HttpResponseRedirect(url)


def index(request):
    current_session_valid = False
    if "user_key" in request.session.keys():
        current_session_valid = True
        username = signing.loads(request.session["user_key"])
    if current_session_valid:
        context = {
            "page_name": "CoviGuard",
            "css_name": "login",
            "session_valid": current_session_valid,
            "username": username,
        }
    else:
        context = {
            "page_name": "CoviGuard",
            "css_name": "login",
            "session_valid": current_session_valid,
        }
    return render(request, "login/index.html", context)


def signin(request):

    if request.method == "POST" and "sign-in" in request.POST:
        try:
            username = request.POST.get("username")
            hasher = PBKDF2WrappedSHA1PasswordHasher()
            password = hasher.encode(request.POST.get("password"), "test123")
            user = UserData.objects.get(username=username)
            user_enc = signing.dumps(username)
            request.session["user_key"] = user_enc
            if user.password == password:
                url = reverse("circle:dashboard", kwargs={"username": username})
                return HttpResponseRedirect(url)
            else:
                raise Exception("Invalid Password")
        except Exception:
            messages.error(request, "Invalid Username or Password")

    context = {"page_name": "Sign in"}
    return render(request, "login/signin.html", context)


def signup(request):

    context = {"page_name": "SignUp"}

    try:
        if request.method == "POST" and "signup-button" in request.POST:

            if request.POST.get("password") != request.POST.get("confirmpassword"):
                messages.error(request, "Password Do Not Match!!")
                return render(request, "login/signup.html", context)

            userdata = UserData()
            userdata.firstname = request.POST.get("firstname")
            userdata.lastname = request.POST.get("lastname")
            userdata.username = request.POST.get("username")
            userdata.email = request.POST.get("email")
            hasher = PBKDF2WrappedSHA1PasswordHasher()
            userdata.password = hasher.encode(request.POST.get("password"), "test123")
            userdata.save()

            privacy = Privacy()
            privacy.username = UserData.objects.get(
                username=request.POST.get("username")
            )
            privacy.save()

            return HttpResponseRedirect(reverse("login:signin"))
    except Exception:
        url = reverse("login:error")
        return HttpResponseRedirect(url)

    return render(request, "login/signup.html", context)


def logout(request):
    del request.session["user_key"]

    return HttpResponseRedirect(reverse("login:index"))


def error(request):
    return render(request, "login/error.html")
