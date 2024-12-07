from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Incident, IncidentUpdate
from django.utils import timezone

@login_required
def incident_list(request):
    incidents = Incident.objects.all().order_by('-reported_at')
    return render(request, 'incidents/incident_list.html', {
        'incidents': incidents
    })

@login_required
def incident_detail(request, incident_id):
    incident = get_object_or_404(Incident, id=incident_id)
    updates = incident.incidentupdate_set.all().order_by('-timestamp')
    return render(request, 'incidents/incident_detail.html', {
        'incident': incident,
        'updates': updates
    })

@login_required
def incident_create(request):
    if not request.user.can_manage_incidents():
        messages.error(request, 'You do not have permission to create incidents.')
        return redirect('incident_list')
    
    if request.method == 'POST':
        # Handle form submission
        title = request.POST.get('title')
        description = request.POST.get('description')
        priority = request.POST.get('priority')
        location = request.POST.get('location')
        
        incident = Incident.objects.create(
            title=title,
            description=description,
            priority=priority,
            location=location,
            reported_by=request.user,
            reported_at=timezone.now()
        )
        
        messages.success(request, 'Incident created successfully.')
        return redirect('incident_detail', incident_id=incident.id)
    
    return render(request, 'incidents/incident_form.html')
