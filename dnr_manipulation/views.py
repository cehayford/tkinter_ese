from django.shortcuts import render, redirect
from .forms import *
from core.thumbnails import *
from django.core.files.base import ContentFile
from django.contrib.messages import *
from django.views.generic import ListView

def home(request):
    context = {
        'title': 'Home Page',
        'message': 'Welcome to the Home Page!'
    }
    return render(request, 'dnr_manipulation/dashboard/main_dbd.html', context)


def donor_center_dashboard(request):
    render(request, 'dnr_manipulation/dashboard/donor_center.html')


def add_donor(request):
    if request.method == 'POST':
        form = DonorForm(request.POST, request.FILES)
        if form.is_valid():
            donor = form.save(commit=False)
            if donor.medicial_report:
                donor.save()
                success(request, "Donor added successfully")
                file_path = donor.medicial_report.path
                thumbnail = generate_thumbnail(file_path)
                donor.medicial_report.save(f'{donor.donor_name}_thumbnail.jpg', ContentFile(thumbnail))
                return redirect('dnr_manipulation:home')
            else:
                warning(request, "Upload a medical report")
    else:
        form = DonorForm()
    context = {'title': 'Add Donor', 'form': form}
    return render(request, 'dnr_manipulation/donor_entry.html', context)


def transfusion_center_dashboard(request):
    render(request, 'dnr_manipulation/dashboard/transfusion_center.html')


def blood_request(request):
    if request.method == 'POST':
        form = BloodRequestForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(commit=False)
            form.save()
        else:
            return redirect('home')
    else:
        form = BloodRequestForm()
    context = {
        'title': 'Blood Request',
        'message': 'Welcome to the Blood Request Page!',
        'form': form
    }
    return render(request, 'dnr_manipulation/unit_request.html', context)




class donor_view(ListView):
    model = Donor
    template_name = 'dnr_manipulation/donor_info/donor_list.html'
    context_object_name = 'donors'
    ordering = ['last_donation_date']
    paginate_by = 10

    def get_queryset(self):
        return Donor.objects.all()
    