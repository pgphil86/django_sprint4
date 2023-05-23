from django import forms

from .models import Comment, Post, User


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author', )
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'})
        }


class ProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['id', 'username', 'last_name', 'email']


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ['text', ]
