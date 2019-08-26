from .base import *

from events.models import EventEmailConfirmation

class EventEmailConfirmationForm(forms.ModelForm):

	class Meta:
		model = EventEmailConfirmation
		fields = [
			"message",
		]


		widgets = {

				"message": forms.Textarea(
						attrs={
							"class":"form-control m-input",
							"placeholder":"Enter a message to send to your attendees",
							"rows": '3',
                            "oninput": 'ChangeText(this)',
							'maxlength': '600',
                            'required': True,
						}
					),
			}