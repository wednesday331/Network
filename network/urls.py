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
    path("profilepage/<str:username>", views.profilepage, name="profilepage"),
    path("profilepage/configuration/<str:username>", views.configuration, name="configuration"),
    path("profilepage/<str:username>/createdpost", views.createdpost, name="createdpost"),
    url(r'^postlikes/$', views.postlikes, name='postlikes')
]
