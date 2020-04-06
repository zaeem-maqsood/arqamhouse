from .base import *
from events.models import EventResource
from froala_editor.widgets import FroalaEditor



class ResourceFileForm(forms.ModelForm):

    class Meta:
        model = EventResource
        fields = [
            "name", "file", 
        ]

        widgets = {

                    "name": forms.TextInput(
                        attrs={
                            "class": "validate-required",
                            "placeholder": "File Name",
                            "required": True,
                            "maxlength": '100',
                        }
                    ),

                    "file": forms.FileInput(
                        attrs={
                            "required": True,
                            "class": "",
                        }
                    ),

                }




class ResourceImageForm(forms.ModelForm):

    class Meta:
        model = EventResource
        fields = [
            "name", "image", 
        ]

        widgets = {

                    "name": forms.TextInput(
                        attrs={
                            "class": "validate-required",
                            "placeholder": "File Name",
                            "required": True,
                            "maxlength": '100',
                        }
                    ),

                    "image": forms.FileInput(
                        attrs={
                            "onchange": "document.getElementById('image-placeholder').src = window.URL.createObjectURL(this.files[0])",
                            "class": "validate-required",
                        }
                    ),

                }



class ResourceLinkForm(forms.ModelForm):

    class Meta:
        model = EventResource
        fields = [
            "name", "link",
        ]

        widgets = {

                    "name": forms.TextInput(
                        attrs={
                            "class": "validate-required",
                            "placeholder": "File Name",
                            "required": True,
                            "maxlength": '100',
                        }
                    ),

                    "link": forms.TextInput(
                        attrs={
                            "placeholder": "https://www.some-link-goes-here.com",
                            "class": "validate-required",
                        }
                    ),

                }


class ResourceTextForm(forms.ModelForm):

    text = forms.CharField(required=False, widget=FroalaEditor(options={
                                  'toolbarInline': False, 'attribution': False, 'tableStyles': 'table', 'pastePlain': True}))

    class Meta:
        model = EventResource
        fields = [
            "name", "text",
        ]

        widgets = {

                    "name": forms.TextInput(
                        attrs={
                            "class": "validate-required",
                            "placeholder": "File Name",
                            "required": True,
                            "maxlength": '100',
                        }
                    ),

                }
