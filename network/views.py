from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.utils import InternalError
from django.http import HttpResponse, HttpResponseRedirect
from django.http.response import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.core.paginator import Paginator
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required


from .models import User, Post, UserFollowing
from .utils import follow_check, sort_by_date_reverse

class NewPost(forms.Form):
    content = forms.CharField(label = "Content", required = True, widget = forms.Textarea)

def index(request):

    if request.method == "GET":
        # Get all the available posts and sort them by date 
        posts = sort_by_date_reverse(Post.objects.all())
        paginator = Paginator(posts,10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
   
    # Create a new Post object  
    if request.method == "POST":
        newPost = NewPost(request.POST)

        if newPost.is_valid():
            content = newPost.cleaned_data["content"]
            user = request.user
            post = Post (content = content, author = user)
            post.save()      

            # Get the updated list of posts and sort them by date 
            posts = sort_by_date_reverse(Post.objects.all())
            paginator = Paginator(posts,10)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
             

    return render(request, "network/index.html", { "postForm":NewPost(), "posts":page_obj})


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
        return render(request, "network/login.html")


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
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
        
@csrf_exempt
@login_required
def post(request, post_id):
    #Query for requested post
    try:
        post = Post.objects.get(pk = post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found"}, status = 404)
    
    # Return post contents
    if request.method == "GET":
        return JsonResponse(post.serialize())
 
    elif request.method == "PUT":
        data = json.loads(request.body)

        # Update the number of likes for the post
        if data.get("likedBy") is not None:
                likedBy = User.objects.get(username = data["likedBy"])
        if data.get("addLiker") is not None:        
                if data.get("addLiker") == True:
                    post.likedBy.add(likedBy)
                else:
                    post.likedBy.remove(likedBy)   
                post.save()  
                
        # Edit post content 
        if data.get("content") is not None:
                if request.user != post.author: 
                    return JsonResponse({"error":"The post you are trying to edit belongs to a different user"}, status = 401)
                else: 
                    post.content = data["content"]
                    post.save()
        return HttpResponse(status = 204)
     
    # Delete the post
    elif request.method == "DELETE":
        if request.user != post.author:
            return JsonResponse({"error":"The post you are trying to delete belongs to a different user"}, status = 401) 
        else: 
            post.delete()           
            return HttpResponse(status = 204)   
       

    else:
        return JsonResponse({
            "error": "GET, PUT or DELETE request required"}, status = 400
        )

def profile(request, username):
    #Get the user that is being looked up 
    userToView = User.objects.get(username = username)

    #Access the selected user's posts and sort them in reverse order
    posts = sorted(userToView.posts.all(), key = lambda p:(p.date), reverse=True)
    paginator = Paginator(posts,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
  
    # Get the number of users that follow the selected user
    followers = userToView.followers.all() 
    numFollowers = len(followers)
    
    # Get the number of users the selected user is following
    following = userToView.following.all()
    numFollowing = len(following)

    # Provide default text for the "follow" button 
    buttonText = "Follow"

    # Check if the user is logged in
    user = request.user
    if user.is_authenticated:
    
        # Reset the "follow" button if the logged in user is already following the selected user 
         if follow_check(user, userToView):
            buttonText = "Unfollow"         

    return render(request, "network/profile.html", {"userToView":userToView.username, "posts":page_obj, "numFollowers":numFollowers, "numFollowing":numFollowing, "buttonText":buttonText})

@login_required
def follow(request, username):
    user = request.user

    # Get the user to follow/unfollow 
    followedUser = User.objects.get(username = username)
   
    if follow_check(user, followedUser): 
        # Unfollow if the logged in user is currently following the viewed user
        followingToRemove = UserFollowing.objects.filter(user = user, followedUser = followedUser)
        followingToRemove.delete()
    else:
        # Follow if the logged in user is currently following the viewed user
        newFollowing = UserFollowing(user = user, followedUser = followedUser)
        newFollowing.save()

    return HttpResponseRedirect(reverse("profile", args = (username,)))

@login_required
def following(request):
    posts = []
        
    # Get the users that the logged in user is following
    followedUsers = [f.followedUser for f in request.user.following.all()]
        
    # Get all the posts by the followed users    
    for followedUser in followedUsers:
        
        for post in followedUser.posts.all():
            posts.append(post)

    # Sort posts by date 
    posts = sort_by_date_reverse(posts)
    paginator = Paginator(posts,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/following.html", {"posts":page_obj}) 





        
