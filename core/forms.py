from django import forms

class ContactForm(forms.Form):
    # Added widgets for Bootstrap form styling for consistency
    name = forms.CharField(
        max_length=100, 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Full Name'})
    )
    email = forms.EmailField(
        required=True, 
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your.email@example.com'})
    )
    # The subject field is now included and made optional (though required in template for reCAPTCHA handling)
    subject = forms.CharField(
        max_length=255, 
        required=True, # Made required here to match template and previous logic, but you can change this to False if it's truly optional
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject of your message'})
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Write your message here...'}), 
        required=True
    )
    # Note: reCAPTCHA is handled directly in the template's JavaScript and not explicitly in this form class.
