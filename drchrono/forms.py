from django import forms
from django.forms import widgets


# Add your forms here

class CheckInForm(forms.Form):
    """
    Form in check in page.
    """
    first_name = forms.CharField(required=True, widget=forms.TextInput(
        attrs={
            "class": "form-control",
            }
    ))
    last_name = forms.CharField(required=True, widget=forms.TextInput(
        attrs={
            "class": "form-control",
            }
    ))
    social_security_number = forms.CharField(required=False, widget=forms.TextInput(
        attrs={
            "class": "form-control",
            "placeholder": "XXX-XX-XXXX(optional)"
            }
    ))


class InformationForm(forms.Form):
    """
    Form in demographic information page.
    """
    social_security_number = forms.CharField(required=False, widget=forms.TextInput(
        attrs={
            "placeholder": "XXX-XX-XXXX"
            }
    ))

    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(
        attrs={
            "class": "form-control",
            "type": "date"
            }
    ))
    gender = forms.ChoiceField(required=False, choices=(
        ('', 'Select'),
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    ))

    race = forms.ChoiceField(required=False, choices=(
        ('blank', ''),
        ('indian', 'American Indian or Alaska Native'),
        ('asian', 'Asian'),
        ('black', 'Black or African American'),
        ('hawaiian', 'Native Hawaiian or Other Pacific Islander'),
        ('white', 'White'),
        ('declined', 'Decline to specify')
    ))

    ethnicity = forms.ChoiceField(required=False, choices=(
        ('blank', ''),
        ('hispanic', 'Hispanic or Latino'),
        ('not_hispanic', 'Not Hispanic or Latino'),
        ('declined', 'Declined to specify')
    ))

    address = forms.CharField(required=False)
    
    zip_code = forms.CharField(required=False)

    city = forms.CharField(required=False)

    state = forms.ChoiceField(required=False, choices=(
        ('', '-Select a State-'),
        ('AL', 'Alabama'),
        ('AK', 'Alaska'),
        ('AS', 'American Samoa'),
        ('AZ', 'Arizona'),
        ('AR', 'Arkansas'),
        ('AA', 'Armed Forces Americas'),
        ('AE', 'Armed Forces Europe'),
        ('AP', 'Armed Forces Pacific'),
        ('CA', 'California'),
        ('CO', 'Colorado'),
        ('CT', 'Connecticut'),
        ('DE', 'Delaware'),
        ('DC', 'District of Columbia'),
        ('FL', 'Florida'),
        ('GA', 'Georgia'),
        ('GU', 'Guam'),
        ('HI', 'Hawaii'),
        ('ID', 'Idaho'),
        ('IL', 'Illinois'),
        ('IN', 'Indiana'),
        ('IA', 'Iowa'),
        ('KS', 'Kansas'),
        ('KY', 'Kentucky'),
        ('LA', 'Louisiana'),
        ('ME', 'Maine'),
        ('MD', 'Maryland'),
        ('MA', 'Massachusetts'),
        ('MI', 'Michigan'),
        ('MN', 'Minnesota'),
        ('MS', 'Mississippi'),
        ('MO', 'Missouri'),
        ('MT', 'Montana'),
        ('NE', 'Nebraska'),
        ('NV', 'Nevada'),
        ('NH', 'New Hampshire'),
        ('NJ', 'New Jersey'),
        ('NM', 'New Mexico'),
        ('NY', 'New York'),
        ('NC', 'North Carolina'),
        ('ND', 'North Dakota'),
        ('MP', 'Northern Mariana Islands'),
        ('OH', 'Ohio'),
        ('OK', 'Oklahoma'),
        ('OR', 'Oregon'),
        ('PA', 'Pennsylvania'),
        ('PR', 'Puerto Rico'),
        ('RI', 'Rhode Island'),
        ('SC', 'South Carolina'),
        ('SD', 'South Dakota'),
        ('TN', 'Tennessee'),
        ('TX', 'Texas'),
        ('UT', 'Utah'),
        ('VT', 'Vermont'),
        ('VI', 'Virgin Islands'),
        ('VA', 'Virginia'),
        ('WA', 'Washington'),
        ('WV', 'West Virginia'),
        ('WI', 'Wisconsin'),
        ('WY', 'Wyoming')
    ))

    email = forms.EmailField(required=False)

    cell_phone = forms.CharField(required=False)

    emergency_contact_name = forms.CharField(required=False)

    emergency_contact_phone = forms.CharField(required=False)

    emergency_contact_relation = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        """
        Initialize class in each field.
        """
        super(InformationForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
