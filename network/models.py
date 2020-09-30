#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Registered classes for the Network Project"""

# Register your models here.
from datetime import datetime
from django.contrib.auth.models import AbstractUser
from django.db import models

# User class
class User(AbstractUser):
    """Abstract class for users to be used in views.py"""
    pass

# Post class
class Post(models.Model):
    """Post components for each post in the network."""
    content = models.CharField(max_length=255)
    user = models.ForeignKey('User',
                             on_delete=models.CASCADE,
                             related_name='author')
    date = models.DateTimeField(default=datetime.now())
    thumbsuped = models.ManyToManyField('User',
                                        default=None,
                                        blank=True,
                                        related_name='postlikesno')

    @property
    def likes_number(self):
        return self.thumbsuped.all().count()

# Profile Class    
class Profile(models.Model):
    """Profile information components."""
    target = models.ForeignKey('User',
                               on_delete=models.CASCADE,
                               related_name='followers')
    follower = models.ForeignKey('User',
                                 on_delete=models.CASCADE,
                                 related_name='targets')
# Like/Dislike Class
class Like(models.Model):
    """Class for liking/disliking posts."""
    user = models.ForeignKey('User',
                             on_delete=models.CASCADE)
    post = models.ForeignKey('Post',
                             on_delete=models.CASCADE)

    def __str__(self):
        return str(self.post)
