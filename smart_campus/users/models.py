from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """Custom user model with additional fields for security system"""
    
    ROLE_CHOICES = (
        ('admin', _('Administrator')),
        ('security_officer', _('Security Officer')),
        ('supervisor', _('Supervisor')),
        ('operator', _('Operator')),
        ('viewer', _('Viewer')),
    )
    
    role = models.CharField(_('Role'), max_length=20, choices=ROLE_CHOICES, default='viewer')
    department = models.CharField(_('Department'), max_length=100, blank=True)
    employee_id = models.CharField(_('Employee ID'), max_length=50, unique=True, blank=True, null=True)
    phone_number = models.CharField(_('Phone Number'), max_length=20, blank=True)
    is_active_duty = models.BooleanField(_('Active Duty'), default=False)
    last_login_ip = models.GenericIPAddressField(_('Last Login IP'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
    
    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"
    
    def has_role(self, role):
        """Check if user has specific role"""
        return self.role == role
    
    def is_admin(self):
        """Check if user is administrator"""
        return self.role == 'admin'
    
    def is_security_officer(self):
        """Check if user is security officer"""
        return self.role == 'security_officer'
    
    def can_view_cameras(self):
        """Check if user can view camera feeds"""
        return self.role in ['admin', 'security_officer', 'supervisor', 'operator']
    
    def can_manage_incidents(self):
        """Check if user can manage incidents"""
        return self.role in ['admin', 'security_officer', 'supervisor']

class UserActivity(models.Model):
    """Model for tracking user activity in the system"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(_('Activity Type'), max_length=50)
    description = models.TextField(_('Description'))
    ip_address = models.GenericIPAddressField(_('IP Address'))
    timestamp = models.DateTimeField(_('Timestamp'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('User Activity')
        verbose_name_plural = _('User Activities')
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type}"
