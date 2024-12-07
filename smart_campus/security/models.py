from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Camera(models.Model):
    """Model for managing security cameras"""
    
    CAMERA_TYPES = (
        ('fixed', _('Fixed')),
        ('ptz', _('Pan-Tilt-Zoom')),
        ('dome', _('Dome')),
    )
    
    STATUS_CHOICES = (
        ('active', _('Active')),
        ('inactive', _('Inactive')),
        ('maintenance', _('Under Maintenance')),
    )
    
    name = models.CharField(_('Camera Name'), max_length=100)
    location = models.CharField(_('Location'), max_length=200)
    camera_type = models.CharField(_('Camera Type'), max_length=20, choices=CAMERA_TYPES)
    ip_address = models.GenericIPAddressField(_('IP Address'))
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='active')
    is_recording = models.BooleanField(_('Recording Status'), default=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Camera')
        verbose_name_plural = _('Cameras')
    
    def __str__(self):
        return f"{self.name} - {self.location}"

class AccessLog(models.Model):
    """Model for tracking access to camera feeds"""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
    accessed_at = models.DateTimeField(_('Accessed At'), auto_now_add=True)
    action = models.CharField(_('Action'), max_length=50)
    ip_address = models.GenericIPAddressField(_('IP Address'))
    
    class Meta:
        verbose_name = _('Access Log')
        verbose_name_plural = _('Access Logs')
        ordering = ['-accessed_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.camera.name} - {self.action}"

class SecurityZone(models.Model):
    """Model for defining security zones"""
    
    SECURITY_LEVELS = (
        ('high', _('High Security')),
        ('medium', _('Medium Security')),
        ('low', _('Low Security')),
    )
    
    name = models.CharField(_('Zone Name'), max_length=100)
    description = models.TextField(_('Description'))
    security_level = models.CharField(_('Security Level'), max_length=20, choices=SECURITY_LEVELS)
    cameras = models.ManyToManyField(Camera, related_name='zones')
    is_active = models.BooleanField(_('Active Status'), default=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Security Zone')
        verbose_name_plural = _('Security Zones')
    
    def __str__(self):
        return f"{self.name} - {self.security_level}"
