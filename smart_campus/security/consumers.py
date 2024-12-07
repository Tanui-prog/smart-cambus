import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
from django.utils import timezone
from .models import Camera, SecurityZone, AccessLog
from incidents.models import Incident

class SecurityConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Join security group
        await self.channel_layer.group_add(
            "security_updates",
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave security group
        await self.channel_layer.group_discard(
            "security_updates",
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Receive message from WebSocket.
        """
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'camera_status_update':
            await self.handle_camera_status_update(data)
        elif message_type == 'incident_report':
            await self.handle_incident_report(data)

    async def security_update(self, event):
        """
        Receive security update from group.
        """
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def update_camera_status(self, camera_id, new_status):
        """
        Update camera status in database.
        """
        try:
            camera = Camera.objects.get(id=camera_id)
            camera.status = new_status
            camera.save()
            return camera
        except Camera.DoesNotExist:
            return None

    async def handle_camera_status_update(self, data):
        """
        Handle camera status updates.
        """
        camera_id = data.get('camera_id')
        new_status = data.get('status')
        
        camera = await self.update_camera_status(camera_id, new_status)
        if camera:
            # Broadcast update to all connected clients
            await self.channel_layer.group_send(
                "security_updates",
                {
                    "type": "security_update",
                    "message_type": "camera_status_update",
                    "camera_id": camera_id,
                    "camera_name": camera.name,
                    "status": new_status,
                    "location": camera.location
                }
            )

    @database_sync_to_async
    def create_incident(self, incident_data):
        """
        Create new incident in database.
        """
        try:
            incident = Incident.objects.create(
                title=incident_data.get('title'),
                description=incident_data.get('description'),
                priority=incident_data.get('priority'),
                location=incident_data.get('location'),
                reported_by_id=incident_data.get('reported_by')
            )
            return incident
        except Exception as e:
            print(f"Error creating incident: {str(e)}")
            return None

    async def handle_incident_report(self, data):
        """
        Handle new incident reports.
        """
        incident_data = data.get('incident')
        incident = await self.create_incident(incident_data)
        
        if incident:
            # Broadcast incident to all connected clients
            await self.channel_layer.group_send(
                "security_updates",
                {
                    "type": "security_update",
                    "message_type": "new_incident",
                    "incident_id": incident.id,
                    "title": incident.title,
                    "priority": incident.priority,
                    "location": incident.location,
                    "reported_by": incident.reported_by.get_full_name()
                }
            )

class CameraConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.camera_id = self.scope['url_route']['kwargs']['camera_id']
        self.camera_group_name = f'camera_{self.camera_id}'

        # Join camera-specific group
        await self.channel_layer.group_add(
            self.camera_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave camera-specific group
        await self.channel_layer.group_discard(
            self.camera_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Receive message from WebSocket.
        """
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'motion_detected':
            await self.handle_motion_detection(data)

    async def camera_update(self, event):
        """
        Receive camera update from group.
        """
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def log_motion_detection(self, details):
        """
        Create a motion detection log entry in the database.
        Returns the camera object and timestamp if successful, (None, None) otherwise.
        """
        try:
            camera = Camera.objects.get(id=self.camera_id)
            log = camera.accesslog_set.create(
                action="Motion Detected",
                details=details,
                timestamp=timezone.now()
            )
            return camera, log.timestamp
        except Camera.DoesNotExist:
            return None, None
        except Exception as e:
            print(f"Error logging motion detection: {str(e)}")
            return None, None

    async def handle_motion_detection(self, data):
        """
        Handle motion detection events and broadcast to relevant clients.
        """
        details = data.get('details', '')
        camera, timestamp = await self.log_motion_detection(details)
        
        if camera and timestamp:
            # Broadcast motion detection to all clients watching this camera
            await self.channel_layer.group_send(
                self.camera_group_name,
                {
                    "type": "camera_update",
                    "message_type": "motion_detected",
                    "camera_id": self.camera_id,
                    "camera_name": camera.name,
                    "location": camera.location,
                    "timestamp": timestamp.isoformat(),
                    "details": details
                }
            )
