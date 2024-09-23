from django.contrib import messages
from django.shortcuts import render, redirect
from validate_email import validate_email

from contact.models import Contact


def contact_us(request):
    if request.method == 'POST':
        context = {'has_error': False, 'data': request.POST}
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        if not name:
            messages.add_message(request, messages.ERROR,
                                 'Name is required')
            context['has_error'] = True

        if not email:
            messages.add_message(request, messages.ERROR,
                                 'Email is required')
            context['has_error'] = True

        if not validate_email(email):
            messages.add_message(request, messages.ERROR,
                                 'Enter a valid email address')
            context['has_error'] = True

        if not subject:
            messages.add_message(request, messages.ERROR,
                                 'Add a subject')
            context['has_error'] = True

        if not message:
            messages.add_message(request, messages.ERROR,
                                 'Type you question or suggestion')
            context['has_error'] = True

        if context['has_error']:
            return render(request, 'contact_us/contact_us.html', context)

        new_contact = Contact(full_names=name, email=email, subject=subject, message=message)
        new_contact.save()

        messages.add_message(request, messages.SUCCESS,
                             'Message sent successfully')
        return redirect('contact:contact')
    return render(request, 'contact_us/contact_us.html')
