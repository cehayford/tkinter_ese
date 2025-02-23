from django.db import models
from datetime import timedelta


class BloodGroup(models.Model):
    blood_type = models.CharField(max_length=3)
    can_give_to = models.ManyToManyField('self', related_name='can_receive_from', symmetrical=False)

    def __str__(self):
        return self.blood_type
    

class Donor(models.Model):
    donor_name = models.CharField(max_length=200)
    blood_type = models.ForeignKey(BloodGroup, on_delete=models.PROTECT)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    location = models.CharField(max_length=450)
    last_donation_date = models.DateField(null=True, blank=True)
    medicial_report = models.FileField(upload_to='donor_reports/')
    date_donated = models.DateField(auto_now= True)
    is_available = models.BooleanField(default=True)

    
    def __str__(self):
        return f"{self.donor_name}"
    

class TransfusionCenter(models.Model):
    donor = models.ForeignKey(Donor, on_delete=models.PROTECT)
    donation_date = models.DateField()
    expiry_date = models.DateField()
    center_name = models.CharField(max_length=450)
    location = models.CharField(max_length=450)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    blood_type = models.ForeignKey(BloodGroup, on_delete=models.PROTECT)
    is_available = models.BooleanField(default=True)
        
    def __str__(self):
        return f"{self.center_name}"
        
    def save(self, *args, **kwargs):
        if self.donor:
            self.donation_date = Donor.date_donated
        if not self.expiry_date:
            self.expiry_date = self.collection_date + timedelta(days=42)
        super().save(*args, **kwargs)


class BloodRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('COMPLETED', 'Completed'),
        ('REJECTED', 'Rejected')
    ]
    patient_name = models.CharField(max_length=200)
    blood_group = models.ForeignKey(BloodGroup, on_delete=models.PROTECT)
    quantity_ml = models.IntegerField()
    hospital = models.CharField(max_length=450)
    location = models.CharField(max_length=450)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.ManyToManyField(TransfusionCenter, blank=True)

    def get_can_give_blood_from(self):
        return self.blood_group.can_receive_from.all()