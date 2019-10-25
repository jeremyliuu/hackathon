from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView
from django.utils import timezone
from social_django.models import UserSocialAuth

from drchrono.endpoints import DoctorEndpoint
from drchrono.endpoints import PatientEndpoint
from drchrono.endpoints import AppointmentEndpoint
from drchrono.models import WaitingDuration
from drchrono.forms import CheckInForm
from drchrono.forms import InformationForm

from datetime import datetime

LEGAL_STATUS = ('Arrived', 'In Session', 'Complete') # Considered status in this demo.
TEST_DATE = datetime(2019, 10, 13, 12, 0) # Set default date for demo.

class SetupView(TemplateView):
    """
    The beginning of the OAuth sign-in flow. Logs a user into the kiosk, and saves the token.
    """
    template_name = 'kiosk_setup.html'


def doctor_welcome(request):
    """
    The doctor can see what appointments they have today.
    """
    # Social Auth module is configured to store our access tokens.
    # This dark magic will fetch it for us if we'vealready signed in.
    oauth_provider = UserSocialAuth.objects.get(provider='drchrono') 
    access_token = oauth_provider.extra_data['access_token']
    api_doctor = DoctorEndpoint(access_token)
    # Grab the first doctor from the list; normally this would be the whole practice group, but your hackathon
    # account probably only has one doctor in it.
    api_appointment = AppointmentEndpoint(access_token)
    api_patient = PatientEndpoint(access_token)
    # Get appointment and patient lists.
    doctor = next(api_doctor.list())[0]
    cur_date = TEST_DATE.strftime('%Y-%m-%d') 
    appointments = next(api_appointment.list(date=cur_date)) # Find appointments today.
    avg_waiting_time, n = 0, 0
    now = timezone.now()
    for appointment in appointments:
        # Fetch patient by patient id in this appointment.
        # Get patient name to show on appointment list.
        patient = api_patient.fetch(id = appointment['patient'])
        appointment['patient_name'] = patient['first_name'] + ' ' + patient['last_name']
        # Show scheduled time in AM/PM.
        appointment['brief_scheduled_time'] = datetime.strptime(appointment['scheduled_time'], '%Y-%m-%dT%H:%M:%S').strftime("%I:%M %p")
        # If status is 'Arrived/In Session/Complete', get waiting time in local model.
        if appointment['status'] in LEGAL_STATUS:
            try:
                waiting = WaitingDuration.objects.get(app_id=appointment['id'])
                if appointment['status'] == 'Arrived':
                    # Only update current time if status is 'Arrived'.
                    waiting.start_time = now
            except WaitingDuration.DoesNotExist:
                # Fix bug: Patient walks in and starts immediately.
                waiting = WaitingDuration(app_id=appointment['id'], arrived_time=now, start_time=now)
            # Calculate average waiting time.
            appointment['waited_time'] = ((waiting.start_time - waiting.arrived_time).seconds) // 60
            waiting.save()
            avg_waiting_time += appointment['waited_time']
            appointment['waited_time_display'] = str(appointment['waited_time']) + ' min'
            n += 1
    context = {}
    new_apps = []
    if request.method == 'POST':
        # Generate list in different status if section buttons are clicked.
        section = request.POST.get("option", "")
        for appointment in appointments:
            if appointment['status'] == section or section == 'All':
                new_apps.append(appointment)
    else:
        new_apps = appointments[:]
    context['doctor'] = doctor
    context['appointment'] = new_apps
    context['avg_time_waited'] = avg_waiting_time if n== 0 else int(avg_waiting_time // n)
    context['today_date'] = TEST_DATE.strftime("%b %d %Y")
    return render(request, 'doctor_welcome.html', context)


def update_status(request):
    """
    update appointment status after doctor click start/finish button.
    """
    oauth_provider = UserSocialAuth.objects.get(provider='drchrono')
    access_token = oauth_provider.extra_data['access_token']    
    api_appointment = AppointmentEndpoint(access_token)
    if request.method == 'POST': 
        appointment_id = request.POST.get("id", "")
        appointment = api_appointment.fetch(id = appointment_id)
        status = request.POST.get("status", "")
        if appointment['status'] == 'Arrived' and status == 'In Session':
            # update status if a patient has arrived and start button is clicked.
            api_appointment.update(appointment_id, {"status": status})
            waiting = WaitingDuration.objects.get(app_id=appointment_id)
            waiting.start_time = timezone.now()
            waiting.save()
        elif appointment['status'] == 'In Session' and status == 'Complete':
            # update status if a patient is in session and finish button is clicked.
            api_appointment.update(appointment_id, {"status": status})
    return redirect('/welcome/')


def check_in_patients(request):
    """
    Show check-in page and verify the information provided by patient.
    """
    form = CheckInForm(request.POST or None)
    oauth_provider = UserSocialAuth.objects.get(provider='drchrono')
    access_token = oauth_provider.extra_data['access_token']
    api_appointment = AppointmentEndpoint(access_token)
    api_patient = PatientEndpoint(access_token)
    if form.is_valid():
        # Get the input information.
        first_name = form.cleaned_data.get('first_name', '')
        last_name = form.cleaned_data.get('last_name', '')
        ssn = form.cleaned_data.get('social_security_number', '')
        cur_date = TEST_DATE.strftime('%Y-%m-%d')
        appointments = next(api_appointment.list(date=cur_date))
        patient_valid = False # Flag for patient information accuracy.
        apps_today = [] # non-check-in appointment list today for this patient. 
        for appointment in appointments:
            patient = api_patient.fetch(id = appointment['patient'])
            if patient['first_name'] == first_name and patient['last_name'] == last_name \
                and ssn in ['', patient['social_security_number']]:
                # Verify the information. And ssn is optional.
                patient_valid = True
                if appointment['status'] not in LEGAL_STATUS:
                    # Put appointment in list if status is not in LEGAL_STATUS, 
                    # which means patient is not arrived yet.
                    appointment['patient_name'] = patient['first_name'] + ' ' + patient['last_name']
                    appointment['brief_scheduled_time'] = datetime.strptime(appointment['scheduled_time'], '%Y-%m-%dT%H:%M:%S').strftime("%b %d %Y %I:%M %p")
                    apps_today.append(appointment)
        if not patient_valid:
            # Show invaild info message if flag is False.
            return render(request, 'patient_check_in.html', {
                'form': form, 
                'message': 'Invalid patient information! Please try again.'
            })
        elif not apps_today:
            # Show no appointments message if list is empty.
            return render(request, 'patient_check_in.html', {
                'form': form, 
                'message': 'You have checked in/No appointments today.'
            })
        else:
            # Go to new appointment list page for this patient.
            return render(request, 'select_appointments.html', {'appointments': apps_today})
    return render(request, 'patient_check_in.html', {'form': form})


def select_appointments(request):
    """
    React after patient choose one appointment.
    """
    if request.method == 'POST':
        # Use session, pass the patient id and appointment id to next page(demographic info page). 
        request.session['patient_id'] = request.POST.get("patient")
        request.session['appointment_id'] = request.POST.get("appointment")
        return redirect('/info/')


def demographic_info(request):
    """
    show demographic infomation and update if info change.
    """
    oauth_provider = UserSocialAuth.objects.get(provider='drchrono')
    access_token = oauth_provider.extra_data['access_token']
    api_patient = PatientEndpoint(access_token)
    patient_id = request.session.get('patient_id')
    request.session['appointment_id'] = request.session.get('appointment_id')
    patient = api_patient.fetch(id = patient_id)
    # Initialize info and put in textbox.
    initial_info = {
        'social_security_number': patient['social_security_number'],
        'date_of_birth': patient['date_of_birth'],
        'gender': patient['gender'],
        'race': patient['race'],
        'ethnicity': patient['ethnicity'],
        'address': patient['address'],
        'zip_code': patient['zip_code'],
        'city': patient['city'],
        'state': patient['state'],
        'email': patient['email'],
        'cell_phone': patient['cell_phone'],
        'emergency_contact_name': patient['emergency_contact_name'],
        'emergency_contact_phone': patient['emergency_contact_phone'],
        'emergency_contact_relation': patient['emergency_contact_relation']
    }
    form = InformationForm(request.POST or None, initial=initial_info)
    if form.is_valid():
        # update the demographic info.
        demo_info = form.cleaned_data
        if request.method == 'POST':
            action = request.POST.get("action", "")
        if action == 'update':
            # update if click update button
            for key in demo_info:
                api_patient.update(patient_id, {key: demo_info.get(key, '')})
        # go to success page when click either update or skip button.
        return redirect('/success/')
    return render(request, 'patient_welcome.html', {'form': form})


def successfully_check_in(request):
    """
    Show message page for patient who check in successfully.
    """
    oauth_provider = UserSocialAuth.objects.get(provider='drchrono')
    access_token = oauth_provider.extra_data['access_token']
    api_appointment = AppointmentEndpoint(access_token)
    appointment_id = request.session.get('appointment_id')
    request.session.clear() # clear session to avoid info leaking.
    api_appointment.update(appointment_id, {'status': 'Arrived'}) # change status to 'Arrived'.
    try:
        # Get waiting time if local model has already.
        waiting = WaitingDuration.objects.get(app_id=appointment_id)
    except WaitingDuration.DoesNotExist:
        # Create waiting time.
        waiting = WaitingDuration(app_id=appointment_id, arrived_time=timezone.now(), start_time=timezone.now())
    waiting.save()
    return render(request, 'successfully_check_in.html')