from django import forms
from .models import BloodGroup, Donor, TransfusionCenter, BloodRequest

class BloodGroupForm(forms.ModelForm):
    class Meta:
        model = BloodGroup
        # fields = ['blood_type']
        fields = ['blood_type', 'can_give_to']

class DonorForm(forms.ModelForm):
    class Meta:
        model = Donor
        fields = ['donor_name', 'blood_type', 'phone', 'email', 'location', 'medicial_report', 'last_donation_date']

class TransfusionCenterForm(forms.ModelForm):
    class Meta:
        model = TransfusionCenter
        fields = '__all__'

class BloodRequestForm(forms.ModelForm):
    class Meta:
        model = BloodRequest
        fields = ['patient_name', 'blood_group', 'quantity_ml','hospital', 'location']