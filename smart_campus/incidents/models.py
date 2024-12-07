from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from security.models import Camera, SecurityZone

class Incident(models.Model):
    """Model for tracking security incidents"""
    
    PRIORITY_LEVELS = (
        ('high', _('High')),
        ('medium', _('Medium')),
        ('low', _('Low')),
    )
    
    STATUS_CHOICES = (
        ('open', _('Open')),
        ('investigating', _('Under Investigation')),
        ('resolved', _('Resolved')),
        ('closed', _('Closed')),
    )
    
    title = models.CharField(_('Title'), max_length=200)
    description = models.TextField(_('Description'))
    location = models.CharField(_('Location'), max_length=200)
    priority = models.CharField(_('Priority'), max_length=20, choices=PRIORITY_LEVELS)
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='open')
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reported_incidents')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_incidents')
    camera = models.ForeignKey(Camera, on_delete=models.SET_NULL, null=True, blank=True)
    zone = models.ForeignKey(SecurityZone, on_delete=models.SET_NULL, null=True, blank=True)
    reported_at = models.DateTimeField(_('Reported At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    resolved_at = models.DateTimeField(_('Resolved At'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('Incident')
        verbose_name_plural = _('Incidents')
        ordering = ['-reported_at']
    
    def __str__(self):
        return f"{self.title} - {self.status}"

class IncidentUpdate(models.Model):
    """Model for tracking updates to incidents"""
    
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='updates')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    update_text = models.TextField(_('Update Text'))
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Incident Update')
        verbose_name_plural = _('Incident Updates')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Update for {self.incident.title} by {self.user.username}"

class Evidence(models.Model):
    """Model for storing evidence related to incidents"""
    
    EVIDENCE_TYPES = (
        ('image', _('Image')),
        ('video', _('Video')),
        ('document', _('Document')),
        ('other', _('Other')),
    )
    
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='evidence')
    title = models.CharField(_('Title'), max_length=200)
    description = models.TextField(_('Description'))
    evidence_type = models.CharField(_('Evidence Type'), max_length=20, choices=EVIDENCE_TYPES)
    file = models.FileField(_('File'), upload_to='evidence/')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(_('Uploaded At'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Evidence')
        verbose_name_plural = _('Evidence')
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.title} - {self.incident.title}"
