from django import forms
from .models import Category, Flashcard

class CategoryForm(forms.ModelForm):
    category_name = forms.CharField(label='Category', required=True)
    
    class Meta:
        model = Category
        fields = ['category_name']

class FlashcardForm(forms.ModelForm):
    form_type = forms.CharField(widget=forms.HiddenInput(), initial="separate_fields")

    class Meta:
        model = Flashcard
        fields = ['question', 'answer', 'category', 'form_type']
        labels = {
            'question': 'Question',
            'answer': 'Answer',
            'category': 'Category',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(FlashcardForm, self).__init__(*args, **kwargs)
        self.fields['category'].required = True
        self.fields['question'].widget.attrs['maxlength'] = 1000
        self.fields['answer'].required = False
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)