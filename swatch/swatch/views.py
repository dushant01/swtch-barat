# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,redirect
from cleanapp.forms import SignUpForm,LoginForm,PostForm,LikeForm,CommentForm
from cleanapp.models import UserModel,SessionToken,PostModel,LikeModel,CommentModel
from imgurpython import ImgurClient
from swatch.settings import BASE_DIR
from django.contrib.auth.hashers import make_password,check_password
from django.http import HttpResponse
import os
from django.core.mail import EmailMessage
from cleanapp.tokens import account_activation_token
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string



# Create your views here.
def homepage_view(request):
	
	return render(request,'homepage.html')

def signup_view(request):
	#bussiness logic
	if request.method == 'GET':
		#display signup form
		form = SignUpForm()
		

	elif request.method == 'POST':
		form = SignUpForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data['username']
			email = form.cleaned_data['email']
			password =form.cleaned_data['password']
			#insert data to database
			new_user=UserModel(username=username, email=email,password=make_password(password))

			new_user.save()
			current_site = get_current_site(request)
            		message = render_to_string('acc_active_email.html', {
                	'user':user, 
                	'domain':current_site.domain,
                	'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                	'token': account_activation_token.make_token(user),
            		})
            		mail_subject = 'Activate your blog account.'
            		to_email = form.cleaned_data.get('email')
            		email = EmailMessage(subject, message, to=[to_email])
            		email.send()
            		return HttpResponse('Please confirm your email address to complete the registration')
    
			
		return redirect("/login/")
		return render(request, 'success.html')
	return render(request, 'signup.html', {'form':form})

def activate(request, uidb64, token):
	try:
		uid = force_text(urlsafe_base64_decode(uidb64))
        	user = User.objects.get(pk=uid)
    	except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        	user = None
    	if user is not None and account_activation_token.check_token(user, token):
        	user.is_active = True
        	user.save()
        	login(request, user)
        	# return redirect('home')
        	return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    	else:
        	return HttpResponse('Activation link is invalid!')


def login_view(request):
	response_data = {}
	if request.method == 'GET':
		#TO DO display login form
		form = LoginForm()		

	elif request.method == 'POST':
		#to doprocess form data
		form = LoginForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data['username']
			password = form.cleaned_data['password']
			#check user is exiting or not in db
			user = UserModel.objects.filter(username=username).filter().first()
			if user:
				#compare password
				if check_password(password, user.password):
					#login succesful
					new_token = SessionToken(user=user)
					new_token.create_token()
					new_token.save()
					response = redirect('/feed/')
					response.set_cookie(key='session_token',value = new_token.session_token)

					return response
				else:
					#password is incorret
					response_data['message'] = 'incorrect Password! please try again!'


	response_data['form'] = form
	return render(request, 'login.html', response_data)



def feed_view(request):
    user = check_validation(request)
    if user:
        posts = PostModel.objects.all().order_by('created_on')
        for post in posts:
            existing_like = LikeModel.objects.filter(post_id=post.id, user=user).first()
            if existing_like:
                post.has_liked = True
        return render(request,'feed.html', { 'posts' : posts})
    else:
        return redirect('/login/')

def check_validation(request):
    if request.COOKIES.get('session_token'): 
        session = SessionToken.objects.filter(session_token=request.COOKIES.get('session_token')).first()
        if session:
            return session.user
        else:
            return None

def post_view(request):
    user = check_validation(request)
    form = PostForm()
    if user:
        if request.method == 'GET':
            form = PostForm()
            return render(request,'post.html',{'form': form})
        elif request.method == 'POST':
            form = PostForm(request.POST,request.FILES)
            if form.is_valid():
                image = form.cleaned_data.get('image')
                caption = form.cleaned_data.get('caption')
                userpost = PostModel(user=user, image=image,caption=caption)
                userpost.save()
                print userpost.image.url
                path = os.path.join(BASE_DIR , userpost.image.url)
                print BASE_DIR
                print path
                client = ImgurClient('b866621832527b5', '296a3fb33f4cfff095f07a8f24f50e930361445c')
                userpost.image_url = client.upload_from_path(path,anon=True)['link']
                userpost.save()
                return redirect('/feed/')
            else:
                form = PostForm()
                return render(request, 'post.html',{'form': form})
    else:
        return redirect('/login/')

def like_view(request):
    user = check_validation(request)
    if user and request.method == 'POST':
        form = LikeForm(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data.get('post').id

            existing_like = LikeModel.objects.filter(post_id=post_id,user=user).first()
           
            if not existing_like:
                LikeModel.objects.create(post_id=post_id, user=user)
            else:
                existing_like.delete()
            return redirect('/feed/')

    else:
        return redirect('/login/')

def comment_view(request):
    user = check_validation(request)
    if user and request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data.get('post').id
            comment_text = form.cleaned_data.get('comment_text')
            comment = CommentModel.objects.create(user=user,post_id=post_id,comment_text=comment_text)
            comment.save()
            return redirect('/feed/')
        else:
            return redirect('/feed/')
    else:
        return redirect('/login/')


