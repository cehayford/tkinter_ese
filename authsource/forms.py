from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser
from django.contrib.auth.password_validation import validate_password


class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=True, validators=[validate_password])
    confirmPassword = forms.CharField(widget=forms.PasswordInput, label='Confirm Password', required=True, validators=[validate_password])
    class Meta:
        model = CustomUser
        fields = [ 'email', 'password']

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('confirmPassword')
        if password and password2 and password != password2:
            raise forms.ValidationError('Password does not match')
        return password
    
    #function to set user to false until account is verified
    def save(self, commit=True):
        user = super(SignupForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.is_active = False
            user.save()
        return user
    

class PasswordChangeForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'autocomplete': 'new-password'}),
        label='New Password',
        validators=[validate_password]
    )
    confirmPassword = forms.CharField(widget=forms.PasswordInput(
        attrs={'autocomplete': 'new-password'}),
        label='New Confirm Password',
        validators=[validate_password]
    )
    
    class Meta:
        model = CustomUser
        fields = []

    def save(self, commit=True):
        new_password = super(PasswordChangeForm, self).save(commit=False)
        new_password.set_password(self.cleaned_data['password'])
        if commit:
            new_password.save()
        return new_password


class LoginForm(AuthenticationForm):
    pass