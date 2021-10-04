from .models import UserFollowing

def follow_check(user, userToFollow):
     followCheck = UserFollowing.objects.filter(user = user, followedUser = userToFollow).exists()
     return followCheck

def sort_by_date_reverse(posts):
    posts = sorted(posts, key = lambda p: (p.date), reverse = True)
    return posts

