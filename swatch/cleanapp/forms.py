from django import forms
from models import UserModel,PostModel,LikeModel,CommentModel

class SignUpForm(forms.ModelForm):
	class Meta:
		model=UserModel
		fields = [ 'username','email','password']




class LoginForm(forms.ModelForm):
	class Meta:

		model=UserModel
		fields=['email','password']


class PostForm(forms.ModelForm):
	class Meta:
		model = PostModel
		fields = ['image','caption']

class LikeForm(forms.ModelForm):
	class Meta:
		model = LikeModel
		fields = ['post']
class CommentForm(forms.ModelForm):
	class Meta:
		model = CommentModel
		fields = ['comment_text', 'post']

