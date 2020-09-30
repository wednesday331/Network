#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Main python code file to execute for the Network project."""

from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from .models import Like, Post, Profile, User

#Editing Class
class Edit(forms.Form):
    """class to edit the information within the text."""
    text_info = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control'}),
                               label='')

# Function for the Home Page     
def index(request):
    """Home page displaying the posts."""
    posts = Post.objects.all().order_by('id').reverse()
    pagination = Paginator(posts, 10)
    page_no = request.GET.get('page')
    posts = pagination.get_page(page_no)
    return render(request, "network/index.html", {'posts': posts})

#Login
def login_view(request):
    """Contains code for the user to login."""
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

#Logout
def logout_view(request):
    """Contains code for the user to logout."""
    logout(request)
    return HttpResponseRedirect(reverse("index"))

#Register
def register(request):
    """Contains code for the user to register."""
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
            email_exists = User.objects.filter(email=email)
            if not email_exists:
                new_user = User.objects.create_user(username, email, password)
                new_user.save()
            else:
                return render(request, "network/register.html", {
                "message": "*Email is already taked."
            })
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "*Username is already taked."
            })
        login(request, new_user)
        return redirect("configuration", username)
    else:
        if request.user.is_anonymous:
            return render(request,"network/register.html")
        else:
            return redirect('index')

# Profile Page Function
def profile_page(request, username):
    """Contains code for the effective display of a profile page."""
    if request.method == 'GET':
        user_present = request.user
        user = get_object_or_404(User, username=username)
        post_list = Post.objects.filter(user=user).order_by('id').reverse()
        follow = Profile.objects.filter(target=user)
        followed = Profile.objects.filter(follower=user)
        if request.user.is_anonymous:
            return redirect('login')
        else:
            followed_both_ways = Profile.objects.filter(follower=user_present, target=user)
            all_follows = len(follow)
            all_followed = len(followed)
            pagination = Paginator(post_list, 10)
            page_no = request.GET.get('page')
            object = pagination.get_page(page_no)
            text_info = {'posts_no': post_list.count(),
                         'profile_user': user,
                         'posts': object,
                         'follow': follow,
                         'all_follows': all_follows,
                         'followed': followed,
                         'all_followed': all_followed,
                         'followed_both_ways': followed_both_ways
                        }
            return render(request, "network/profilepage.html", textinfo)

    else:
        user_present = request.user
        user = get_object_or_404(User, username=username)
        post_list = Post.objects.filter(user=user).order_by('id').reverse()
        followed_both_ways = Profile.objects.filter(follower=request.user, target=user)
        pagination = Paginator(post_list, 10)
        page_no = request.GET.get('page')
        object = pagination.get_page(page_no)
        if not followed_both_ways:
            follow = Profile.objects.create(target=user, follower=user_present)
            follow.save()
            follow = Profile.objects.filter(target=user)
            followed = Profile.objects.filter(follower=user)
            followed_both_ways = Profile.objects.filter(follower=request.user, target=user)
            all_follows = len(follow)
            all_followed = len(followed)
            text_info = {'posts_no': post_list.count(),
                         'profile_user': user,
                         'posts': object,
                         'follow': follow,
                         'all_follows': all_follows,
                         'followed': followed,
                         'all_followed': all_followed,
                         'followed_both_ways': followed_both_ways
                        }
            return render(request, "network/profilepage.html", text_info)
        else:
            followed_both_ways.delete()
            follow = Profile.objects.filter(target=user)
            followed = Profile.objects.filter(follower=user)
            all_follows = len(follow)
            all_followed = len(followed)
            text_info = {'posts_no': post_list.count(),
                         'profile_user': user,
                         'posts': object,
                         'follow': follow,
                         'all_follows': all_follows,
                         'followed': followed, 
                         'all_followed': all_followed,
                         'followed_both_ways': followed_both_ways
                        }
            return render(request, "network/profilepage.html", text_info)

# Post Likes Function        
def post_likes(request):
    """Contains code for liking/disliking a post."""
    user_profile = request.user
    if request.method == 'GET':
        post_no = request.GET['post_no']
        post_liked = Post.objects.get(pk=post_no)
        if user_profile in post_liked.thumbsuped.all():
            post_liked.thumbsuped.remove(user_profile)
            liked = Like.objects.get(post=post_liked, user=user_profile)
            liked.delete()
        else:
            liked = Like.objects.get_or_create(post=post_liked, user=user_profile)
            post_liked.thumbsuped.add(user_profile)
            post_liked.save()
        return HttpResponse('Success')

#Editing function    
def editing(request, post_no):
    """Contains code to edit a post."""
    if request.method == 'POST':
        post_content = Post.objects.get(pk=post_no)
        text_info = request.POST["text_info"]
        post_content.content = text_info
        post_content.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

#Creating a post    
def created_post(request, username):
    """Contains code to create a post"""
    if request.method == 'POST':
        user = get_object_or_404(User, username=username)
        text_info = request.POST["text_info"]
        if not text_info:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        post = Post.objects.create(content=text_info, user=user)
        post.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

# Follow/Unfollow Function        
def followed(request, username):
    """Contains code to follow/unfollow someone"""
    if request.method == 'GET':
        user_present = get_object_or_404(User, username=username)
        follows = Profile.objects.filter(follower=user_present)
        post_list = Post.objects.all().order_by('id').reverse()
        posted = []
        for p in post_list:
            for follower in follows:
                if follower.target == p.user:
                    posted.append(p)
        if not follows:
            return render(request, 'network/followed.html',
                          {'message': "Opps! You don't follow anybody."})
        pagination = Paginator(posted, 10)
        page_no = request.GET.get('page')
        posts = pagination.get_page(page_no)
        return render(request, 'network/followed.html', {'posts':posts})

# Configuration Function    
def configuration(request, username):
    """Contains code for the configuration settings of a profile."""
    user_profile = request.user
    if request.method == 'GET':
        profile_page = User.objects.get(username=username)
        if request.user.is_anonymous:
            return redirect("login")
        if profile_page.username == user_profile.username:
            return render(request, "network/configuration.html",
                          {'profile_page': profile_page})
        else:
            return redirect("index")
    else:
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email_id = request.POST["email"]
        profile_page = User.objects.get(username=username)
        profile_page.first_name = first_name
        profile_page.last_name = last_name
        email_exists = User.objects.filter(email=email_id)
        if not email_exists or profile_page.email == email_id:
            profile_page.email = email_id
        else:
            return render(request, "network/configuration.html",
                          {'profile_page': profile_page,
                           'message': '*Email already taked.'
                          }
                         )
        profile_page.save()
        return redirect('profile_page', profile_page)

# Delete Function    
def deleting(request, post_no):
    """Contains code to delete a post."""
    post_to_delete = Post.objects.get(pk=post_no)
    if request.method == 'POST':
        post_to_delete.delete()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
