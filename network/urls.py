from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("followed/<str:username>", views.followed, name='followed'),
    path("posts/<int:postno>/editing", views.editing, name="editing"),
    path("<str:postno>/deleting", views.deleting, name="deleting"),
    path("profilepage/<str:username>", views.profile_page, name="profile_page"),
    path("profilepage/configuration/<str:username>", views.configuration, name="configuration"),
    path("profilepage/<str:username>/createdpost", views.created_post, name="created_post"),
    url(r'^postlikes/$', views.post_likes, name='post_likes')
]
