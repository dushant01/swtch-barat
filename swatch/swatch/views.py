# -*- coding: utf-8 -*
# ----------------------------------------here we-import files---------------------------------------------------------------
from __future__ import unicode_literals

from django.shortcuts import render,redirect
from datetime import timedelta
from cleanapp.forms import SignUpForm,LoginForm,PostForm,CommentForm,LikeForm
from cleanapp.models import UserModel, SessionToken, PostModel,CommentModel,LikeModel
from django.contrib.auth.hashers import make_password,check_password
from swatch.settings import BASE_DIR
from django.utils import timezone
from imgurpython import ImgurClient
# Create your views here.
def signup_view(request):
    #------------------------------here is the logic of the functions--------------------------------------------------------
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():

            Username = form.cleaned_data['Username']
            Email =form.cleaned_data['Email']
            
            Password = form.cleaned_data['Password']
            # insert data to db
            new_user = UserModel(Username=username, Email=email, Password=make_password(Password))
            new_user.save()
     #--------------------------here we give conditions which open success page or failed page ----------------------------------
            template_name = 'success.html'
        else:
            template_name = 'failed.html'
    else:
        form = SignUpForm()
        template_name = 'signup.html'

    return render(request, template_name, {'form':form})

#-------------------------------------create a new function for login  user---------------------------------------------------------
def login_view(request):
    #----------------------------------here is the function logic-----------------------------------------------------------------
    if request.method == 'GET':
        #Display Login Page
        login_form = LoginForm()
        template_name = 'login.html'
    #---------------------------------------Elif part---------------------------------------------------------------------------------
    elif request.method == 'POST':
        #Process The Data
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            #Validation Success
            Username = login_form.cleaned_data['Username']
            Password = login_form.cleaned_data['Password']
            #read Data From db
            user = UserModel.objects.filter(Username=Username).first()
            if user:
                #compare Password
                if check_password(Password, user.Password):
                    token = SessionToken(user = user)
                    token.create_token()
                    token.save()
                    response = redirect('feed/')
                    response.set_cookie(key='session_token', value=token.session_token)
                    return response
                    #successfully Login

                    template_name = 'login_success.html'
                else:

                    #Failed
                    template_name = 'login_fail.html'
            else:
                #user doesn't exist
                template_name = 'login_fail.html'
        else:
            #Validation Failed
            template_name = 'login_fail.html'


    return render(request,template_name,{'login_form':login_form})

#-------------------------------------------Create a new function for post --------------------------------------------------------------
def post_view(request):
    #-----------------------------------------here is the function logic------------------------------------------------------------
    user = check_validation(request)

    if user:
        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                image = form.cleaned_data.get('image')
                caption = form.cleaned_data.get('caption')
                post = PostModel(user=user, image=image, caption=caption)
                post.save()

                path = str(BASE_DIR+"//"+post.image.url)

                client = ImgurClient(' b866621832527b5', ' 296a3fb33f4cfff095f07a8f24f50e930361445c')
                post.image_url = client.upload_from_path(path,anon=True)['link']
                post.save()

                return redirect('/feed/')

        else:
            form = PostForm()
        return render(request, 'post.html', {'form' : form})
    else:
        return redirect('/login/')

#--------------------------------------------Create a new functions to show the all post of user--------------------------------------
def feed_view(request):
    user = check_validation(request)
    if user:
        #-------------------------------------here is the functions logic---------------------------------------------------------------

        posts = PostModel.objects.all().order_by('-created_on',)

        for post in posts:

            existing_like = LikeModel.objects.filter(post_id=post.id, user=user).first()
            if existing_like:
                post.has_liked = True


        return render(request, 'feed.html', {'posts': posts})
    else:

        return redirect('/login/')



#----------------------------------------------Create a new functions to like the user post-------------------------------------------
def like_view(request):
    #-------------------------------------------here is the function logic------------------------------------------------------------
    user = check_validation(request)
    if user and request.method == 'POST':
        form = LikeForm(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data.get('post').id
            existing_like = LikeModel.objects.filter(post_id=post_id, user=user).first()
            if not existing_like:
                LikeModel.objects.create(post_id=post_id, user=user)
            else:
                existing_like.delete()

            return redirect('/feed/')

    else:
        return redirect('/login/')

#------------------------------------------------Create a new functions to comment on a user post---------------------------------------
def comment_view(request):
    #----------------------------------------------here is the function logic-------------------------------------------------------
    user = check_validation(request)
    if user and request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data.get('post').id
            comment_text = form.cleaned_data.get('comment_text')
            comment = CommentModel.objects.create(user=user, post_id=post_id, comment_text=comment_text)
            comment.save()
            # TODO: ADD MESSAGE TO INDICATE SUCCESS
            return redirect('/feed/')
        else:
            # TODO: ADD MESSAGE FOR FAILING TO POST COMMENT
            return redirect('/feed/')
    else:
        return redirect('/login')




# -----------------------------------------------Create a functions for validating the session---------------------------------------------
def check_validation(request):
    #----------------------------------------------here is the function logic----------------------------------------------------------
    if request.COOKIES.get('session_token'):
        session = SessionToken.objects.filter(session_token=request.COOKIES.get('session_token')).first()
        if session:
            time_to_live = session.created_on + timedelta(days=1)
            if time_to_live > timezone.now():
                return session.user
    else:
        return None
