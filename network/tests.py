from django.test import Client, TestCase
from .models import Post, User, UserFollowing


# Testing using TestCase

class PostTestCase(TestCase):
    def setUp(self):
    # Create new users
        userA = User.objects.create(username = "AAA", email = "usera@user.user", password = "abcdefg")
        userB = User.objects.create(username = "BBB", email = "userb@user.user", password = "hijklmn")
        userC = User.objects.create(username = "CCC", email = "userc@user.user", password = "opqrstu")
    # Create posts
        Post.objects.create(author = userA, content = "Test post A")
        Post.objects.create(author = userB, content = "Test post B")
        Post.objects.create(author = userB, content = "Test post BB")
    # Create following
        UserFollowing.objects.create(user = userA, followedUser = userB) 
        UserFollowing.objects.create(user = userB, followedUser = userC)
        UserFollowing.objects.create(user = userC, followedUser = userB)

    def test_user_post_count(self):
        b = User.objects.get(username = "BBB")
        self.assertEqual(b.posts.all().count(), 2)     
        
    def test_user_following(self):
        a = User.objects.get(username = "AAA") 
        b = User.objects.get(username = "BBB")
        self.assertEqual(len(b.followers.all()),2)

    def test_index(self):
        c = Client()
        response = c.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["posts"]), 3) 
 
    def test_valid_following_page(self):
        a = User.objects.get(username = "AAA")

        c = Client()
        response = c.get("/AAA")
        self.assertEqual(len(response.context["posts"]), 1)
        self.assertEqual(response.status_code, 200)

    def test_invalid_following_page(self):
        c = Client()
        response = c.get("/DDD/")
        self.assertEqual(response.status_code, 404)
    
 