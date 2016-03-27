from django import forms
from ception.articles.models import Article, ArticleVersion

class ArticleForm(forms.ModelForm):
    status = forms.CharField(widget=forms.HiddenInput())
    title = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), 
        max_length=255)
    content = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control'}), 
        max_length=60000)
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}),
                                  max_length=5000)
    tags = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),
        max_length=255,
        required=False,
        help_text='Use spaces to separate the tags, such as "java jsf primefaces"')

    class Meta:
        model = Article
        fields = ['title', 'content', 'description', 'tags', 'status']

class VersionForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control'}),
        max_length=60000)

    class Meta:
        model = ArticleVersion
        fields = ['content']

class SentenceCommentForm(forms.ModelForm):
    pass