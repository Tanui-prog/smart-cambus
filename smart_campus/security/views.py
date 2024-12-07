from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .models import Camera, SecurityZone
from incidents.models import Incident
from users.models import User
from django.contrib import messages
from django.shortcuts import get_object_or_404
import cv2
import numpy as np
from django.http import StreamingHttpResponse
from django.views.decorators.gzip import gzip_page
from datetime import datetime
from .utils import broadcast_camera_status, broadcast_motion_detection, log_camera_access

# Create your views here.

@login_required
def dashboard(request):
    # Get statistics
    active_cameras_count = Camera.objects.filter(status='active').count()
    open_incidents_count = Incident.objects.filter(status__in=['open', 'investigating']).count()
    zones_count = SecurityZone.objects.filter(is_active=True).count()
    active_officers_count = User.objects.filter(
        role__in=['security_officer', 'supervisor'],
        is_active_duty=True
    ).count()
    
    # Get recent incidents
    recent_incidents = Incident.objects.filter(
        status__in=['open', 'investigating']
    ).order_by('-reported_at')[:5]
    
    # Get cameras with status
    cameras = Camera.objects.all().order_by('-status', 'name')[:10]
    
    context = {
        'active_cameras_count': active_cameras_count,
        'open_incidents_count': open_incidents_count,
        'zones_count': zones_count,
        'active_officers_count': active_officers_count,
        'recent_incidents': recent_incidents,
        'cameras': cameras,
    }
    
    return render(request, 'security/dashboard.html', context)

@login_required
def camera_list(request):
    if not request.user.can_view_cameras():
        messages.error(request, 'You do not have permission to view cameras.')
        return redirect('dashboard')
    
    cameras = Camera.objects.all().order_by('name')
    return render(request, 'security/camera_list.html', {'cameras': cameras})

@login_required
def camera_detail(request, camera_id):
    if not request.user.can_view_cameras():
        messages.error(request, 'You do not have permission to view cameras.')
        return redirect('dashboard')
    
    camera = get_object_or_404(Camera, id=camera_id)
    return render(request, 'security/camera_detail.html', {'camera': camera})

class VideoCamera:
    def __init__(self, camera_id=0):
        self.video = cv2.VideoCapture(camera_id)
        self.camera_id = camera_id
        self.prev_frame = None
        self.motion_threshold = 30  # Adjust this value based on sensitivity needs
        
    def __del__(self):
        self.video.release()
        
    def detect_motion(self, frame):
        """
        Detect motion in frame using frame differencing.
        """
        # Convert frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        
        # Initialize prev_frame if needed
        if self.prev_frame is None:
            self.prev_frame = gray
            return False
            
        # Calculate frame difference
        frame_delta = cv2.absdiff(self.prev_frame, gray)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        
        # Dilate threshold image to fill in holes
        thresh = cv2.dilate(thresh, None, iterations=2)
        
        # Find contours
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Check for significant motion
        significant_motion = False
        for contour in contours:
            if cv2.contourArea(contour) > self.motion_threshold:
                significant_motion = True
                break
                
        # Update previous frame
        self.prev_frame = gray
        
        return significant_motion
        
    def get_frame(self):
        success, image = self.video.read()
        if not success:
            return None
            
        # Detect motion
        if self.detect_motion(image):
            # Broadcast motion detection event
            broadcast_motion_detection(self.camera_id, "Motion detected in camera feed")
            # Add motion indicator to frame
            cv2.putText(image, "Motion Detected", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 
                       1, (0, 0, 255), 2)
            
        # Add timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cv2.putText(image, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Convert to jpg format
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

def gen(camera):
    while True:
        frame = camera.get_frame()
        if frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@gzip_page
@login_required
def camera_feed(request, camera_id):
    if not request.user.can_view_cameras():
        messages.error(request, 'You do not have permission to view camera feeds.')
        return redirect('dashboard')
        
    try:
        # Log camera access
        log_camera_access(
            camera_id=camera_id,
            action="Camera Feed Access",
            details=f"Camera feed accessed from {request.META.get('REMOTE_ADDR')}",
            user=request.user
        )
        
        camera = VideoCamera(camera_id)
        return StreamingHttpResponse(gen(camera),
                                  content_type='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        error_msg = f'Error accessing camera: {str(e)}'
        messages.error(request, error_msg)
        
        # Log access failure
        log_camera_access(
            camera_id=camera_id,
            action="Camera Access Failed",
            details=error_msg,
            user=request.user
        )
        
        return redirect('camera_list')
