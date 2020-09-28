# Register your models here.
from datetime import datetime
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    content = models.CharField(max_length=255)
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='author')
    date = models.DateTimeField(default=datetime.now())
    thumbsuped = models.ManyToManyField('User', default=None, blank=True, related_name='postlikesno')

    @property
    def likesnumber(self):
        return self.thumbsuped.all().count()

class Profile(models.Model):
    target = models.ForeignKey('User', on_delete=models.CASCADE, related_name='followers')
    follower = models.ForeignKey('User', on_delete=models.CASCADE, related_name='targets')

class Like(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.post)
