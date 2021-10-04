from typing import cast
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.fields.related import ForeignKey
from django.utils import timezone

class User(AbstractUser):
    pass

class Post(models.Model):
    content = models.TextField(max_length = 500, blank = False)
    date = models.DateTimeField(default = timezone.now)
    author = models.ForeignKey(User, on_delete = models.CASCADE, null = True, related_name="posts")
    likedBy = models.ManyToManyField(User, blank = True, related_name = "likers")

    def serialize(self):
        return {
            "id":self.id,
            "content":self.content,
            "author":self.author.username,
            "likedBy": [liker.username for liker in self.likedBy.all()],
        }
    def __str__(self):
        return f"Post by {self.author.username}: {self.content[:70]}... "

class UserFollowing(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "following")
    followedUser = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "followers")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user','followedUser'], name = "unique_followers" )
            ]

    def __str__(self):
        return f"{self.user.username} follows {self.followedUser.username}"
