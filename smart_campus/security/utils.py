from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone
from .models import Camera, AccessLog

def broadcast_camera_status(camera_id, status):
    """
    Broadcast camera status update to all connected clients.
    """
    try:
        camera = Camera.objects.get(id=camera_id)
        channel_layer = get_channel_layer()
        
        async_to_sync(channel_layer.group_send)(
            "security_updates",
            {
                "type": "security_update",
                "message_type": "camera_status_update",
                "camera_id": camera_id,
                "camera_name": camera.name,
                "status": status,
                "location": camera.location,
                "timestamp": timezone.now().isoformat()
            }
        )
        return True
    except Camera.DoesNotExist:
        return False
    except Exception as e:
        print(f"Error broadcasting camera status: {str(e)}")
        return False

def broadcast_motion_detection(camera_id, details=""):
    """
    Broadcast motion detection event to relevant clients.
    """
    try:
        camera = Camera.objects.get(id=camera_id)
        timestamp = timezone.now()
        
        # Log the motion detection event
        log = AccessLog.objects.create(
            camera=camera,
            action="Motion Detected",
            details=details,
            timestamp=timestamp
        )
        
        # Broadcast to camera-specific group
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"camera_{camera_id}",
            {
                "type": "camera_update",
                "message_type": "motion_detected",
                "camera_id": camera_id,
                "camera_name": camera.name,
                "location": camera.location,
                "timestamp": timestamp.isoformat(),
                "details": details
            }
        )
        
        # Also broadcast to general security group if high priority
        async_to_sync(channel_layer.group_send)(
            "security_updates",
            {
                "type": "security_update",
                "message_type": "motion_detected",
                "camera_id": camera_id,
                "camera_name": camera.name,
                "location": camera.location,
                "timestamp": timestamp.isoformat(),
                "details": details
            }
        )
        return True
    except Camera.DoesNotExist:
        return False
    except Exception as e:
        print(f"Error broadcasting motion detection: {str(e)}")
        return False

def log_camera_access(camera_id, action, details="", user=None):
    """
    Log camera access event and optionally broadcast it.
    """
    try:
        camera = Camera.objects.get(id=camera_id)
        timestamp = timezone.now()
        
        # Create access log
        log = AccessLog.objects.create(
            camera=camera,
            action=action,
            details=details,
            user=user,
            timestamp=timestamp
        )
        
        # Broadcast access log if it's a significant event
        if action in ["Access Denied", "Unauthorized Access Attempt"]:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "security_updates",
                {
                    "type": "security_update",
                    "message_type": "camera_access_alert",
                    "camera_id": camera_id,
                    "camera_name": camera.name,
                    "location": camera.location,
                    "action": action,
                    "details": details,
                    "timestamp": timestamp.isoformat(),
                    "user": user.get_full_name() if user else "Unknown User"
                }
            )
        return True
    except Camera.DoesNotExist:
        return False
    except Exception as e:
        print(f"Error logging camera access: {str(e)}")
        return False
