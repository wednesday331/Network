from django import forms
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.views.decorators.csrf import csrf_exempt

from .models import User, Post, Profile, Like

class Edit(forms.Form):
    textinfo = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control'}), label='')

def index(request):
    posts = Post.objects.all().order_by('id').reverse()
    pagination = Paginator(posts, 10)
    pageno = request.GET.get('page')
    posts = pagination.get_page(pageno)
    return render(request, "network/index.html", {'posts': posts})

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        if request.user.is_anonymous:
            return render(request, "network/login.html")
        else:
            return redirect('index')


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]


        if not username:
            return render(request, "network/register.html", {
                "message": "*No username."})

        if not email:
            return render(request, "network/register.html", {
                "message": "*No email."})

        if not password:
            return render(request, "network/register.html", {
                "message": "*No password."})

        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "*Passwords must match."})

        # Attempt to create new user
        try:
            emailexists = User.objects.filter(email=email)
            if not emailexists:
                newuser = User.objects.create_user(username, email, password)
                newuser.save()
            else:
                return render(request, "network/register.html", {
                "message": "*Email is already taked."
            })
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "*Username is already taked."
            })
        login(request, newuser)
        return redirect("configuration", username)
    else:
        if request.user.is_anonymous:
            return render(request,"network/register.html")
        else:
            return redirect('index')


def profilepage(request, username):
    if request.method == 'GET':
        userpresent = request.user
        user = get_object_or_404(User, username=username)
        postlist = Post.objects.filter(user=user).order_by('id').reverse()
        follow = Profile.objects.filter(target=user)
        followed = Profile.objects.filter(follower=user)
        if request.user.is_anonymous:
            return redirect('login')
        else:
            followedbothways = Profile.objects.filter(follower=userpresent, target=user)
            allfollows = len(follow)
            allfollowed = len(followed)
            pagination = Paginator(postlist, 10)
            pageno = request.GET.get('page')
            object = pagination.get_page(pageno)
            textinfo = {'postsno': postlist.count(), 'profileuser': user,'posts': object,'follow': follow, 'allfollows': allfollows,'followed': followed, 'allfollowed': allfollowed,'followedbothways': followedbothways}
            return render(request, "network/profilepage.html", textinfo)

    else:
        userpresent = request.user
        user = get_object_or_404(User, username=username)
        postlist = Post.objects.filter(user=user).order_by('id').reverse()
        followedbothways = Profile.objects.filter(follower=request.user, target=user)
        pagination = Paginator(postlist, 10)
        pageno = request.GET.get('page')
        object = pagination.get_page(pageno)
        if not followedbothways:
            follow = Profile.objects.create(target=user, follower=userpresent)
            follow.save()
            follow = Profile.objects.filter(target=user)
            followed = Profile.objects.filter(follower=user)
            followedbothways = Profile.objects.filter(follower=request.user, target=user)
            allfollows = len(follow)
            allfollowed = len(followed)
            textinfo = {'postsno': postlist.count(), 'profileuser': user,'posts': object,'follow': follow, 'allfollows': allfollows,'followed': followed, 'allfollowed': allfollowed,'followedbothways': followedbothways}
            return render(request, "network/profilepage.html", textinfo)
        else:
            followedbothways.delete()
            follow = Profile.objects.filter(target=user)
            followed = Profile.objects.filter(follower=user)
            allfollows = len(follow)
            allfollowed = len(followed)
            textinfo = {'postsno': postlist.count(), 'profileuser': user,'posts': object,'follow': follow, 'allfollows': allfollows,'followed': followed, 'allfollowed': allfollowed,'followedbothways': followedbothways}
            return render(request, "network/profilepage.html", textinfo)

def postlikes(request):
    userprofile = request.user
    if request.method == 'GET':
        postno = request.GET['postno']
        postliked = Post.objects.get(pk=postno)
        if userprofile in postliked.thumbsuped.all():
            postliked.thumbsuped.remove(userprofile)
            liked = Like.objects.get(post=postliked, user=userprofile)
            liked.delete()
        else:
            liked = Like.objects.get_or_create(post=postliked, user=userprofile)
            postliked.thumbsuped.add(userprofile)
            postliked.save()
        return HttpResponse('Success')

def editing(request, postno):
    if request.method == 'POST':
        postcontent = Post.objects.get(pk=postno)
        textinfo = request.POST["textinfo"]
        postcontent.content = textinfo
        postcontent.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def createdpost(request, username):
    if request.method == 'POST':
        user = get_object_or_404(User, username=username)
        textinfo = request.POST["textinfo"]
        if not textinfo:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        post = Post.objects.create(content=textinfo, user=user)
        post.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def followed(request, username):
    if request.method == 'GET':
        userpresent = get_object_or_404(User, username=username)
        follows = Profile.objects.filter(follower=userpresent)
        postlist = Post.objects.all().order_by('id').reverse()
        posted = []
        for p in postlist:
            for follower in follows:
                if follower.target == p.user:
                    posted.append(p)
        if not follows:
            return render(request, 'network/followed.html', {'message': "Opps! You don't follow anybody."})
        pagination = Paginator(posted, 10)
        pageno = request.GET.get('page')
        posts = pagination.get_page(pageno)
        return render(request, 'network/followed.html', {'posts':posts})

def configuration(request, username):
    userprofile = request.user
    if request.method == 'GET':
        profilepage = User.objects.get(username=username)
        if request.user.is_anonymous:
            return redirect("login")
        if profilepage.username == userprofile.username:
            return render(request, "network/configuration.html", {'profilepage': profilepage})
        else:
            return redirect("index")
    else:
        firstname = request.POST["firstname"]
        lastname = request.POST["lastname"]
        emailid = request.POST["email"]
        profilepage = User.objects.get(username=username)
        profilepage.firstname = firstname
        profilepage.lastname = lastname
        emailexists = User.objects.filter(email=emailid)
        if not emailexists or profilepage.email == emailid:
            profilepage.email = emailid
        else:
            return render(request, "network/configuration.html", {'profilepage': profilepage, 'message': '*Email already taked.'})
        profilepage.save()
        return redirect('profilepage', profilepage)

def deleting(request, postno):
    posttodelete = Post.objects.get(pk=postno)
    if request.method == 'POST':
        posttodelete.delete()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
