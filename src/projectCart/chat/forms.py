from django.core.exceptions import NON_FIELD_ERRORS
from django import forms
from .models import ContactUs

class ContactUsForm(forms.ModelForm):
    class Meta:
        model = ContactUs
        fields = ['name', 'email', 'typ', 'messages', 'image']
        error_messages = {
            NON_FIELD_ERRORS: {
                "unique_together": "%(model_name)s's %(field_labels)s are not unique.",
            }
        }

    def __init__(self, *args, **kwargs):
        super(ContactUsForm,self).__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Name", "required": "True" }
        )
        self.fields["email"].widget.attrs.update(
            {"class": "form-control", "placeholder": "@email", "required": "True" }
        )
        
        self.fields["messages"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Messages", "required": "True", "rows":"8","cols":"50" }
        )

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'