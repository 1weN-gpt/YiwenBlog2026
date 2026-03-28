from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 3,
                'placeholder': '写下你的评论...'
            })
        }
        labels = {
            'content': ''
        }


class SearchForm(forms.Form):
    q = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': '搜索文章...'
        }),
        label=''
    )
