

from django import forms
from .models import Post
from django.conf import settings
from core.widgets import ArqamFroalaEditor


class PostForm(forms.ModelForm):

    def __init__(self, house, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
            

        self.fields["content"] = forms.CharField(required=True, widget=ArqamFroalaEditor(options={
            'toolbarInline': False, 'attribution': False, 'tableStyles': 'table', 'pastePlain': True, 'useClasses': False, 'charCounterMax': 2000}, house=house))

    
    test_email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"class": "form-control m-input", "placeholder": "email@domain.com"}), required=False)

    class Meta:
        model = Post
        fields = [
            "name", "content"
        ]


        widgets = {

                "name": forms.TextInput(
                    attrs={
                        "class":"form-control m-input message",
                        "placeholder":"Post Title Goes Here",
                        "required": True,
                        "maxlength": '100',
                        "style": "border: none;background: white;font-size: 20px;text-align: center;"
                    }
                ),
            }
