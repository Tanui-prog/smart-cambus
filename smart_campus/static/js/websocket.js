class SecurityWebSocket {
    constructor() {
        this.connect();
        this.setupReconnection();
    }

    connect() {
        // Use port 8001 for WebSocket connections
        const wsHost = window.location.hostname + ':8001';
        this.ws = new WebSocket(`ws://${wsHost}/ws/security/`);
        this.ws.onopen = () => this.onOpen();
        this.ws.onclose = () => this.onClose();
        this.ws.onmessage = (e) => this.onMessage(e);
        this.ws.onerror = (e) => this.onError(e);
    }

    setupReconnection() {
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000; // Start with 1 second delay
    }

    onOpen() {
        console.log('Connected to security WebSocket');
        this.reconnectAttempts = 0;
        this.reconnectDelay = 1000;
    }

    onClose() {
        console.log('Disconnected from security WebSocket');
        this.attemptReconnect();
    }

    onMessage(e) {
        const data = JSON.parse(e.data);
        
        switch(data.message_type) {
            case 'camera_status_update':
                this.handleCameraUpdate(data);
                break;
            case 'new_incident':
                this.handleNewIncident(data);
                break;
            case 'motion_detected':
                this.handleMotionDetection(data);
                break;
        }
    }

    onError(e) {
        console.error('WebSocket error:', e);
    }

    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            setTimeout(() => {
                console.log(`Attempting to reconnect (${this.reconnectAttempts + 1}/${this.maxReconnectAttempts})`);
                this.connect();
                this.reconnectAttempts++;
                this.reconnectDelay *= 2; // Exponential backoff
            }, this.reconnectDelay);
        } else {
            console.error('Max reconnection attempts reached');
        }
    }

    handleCameraUpdate(data) {
        // Update camera status in UI
        const statusElement = document.querySelector(`#camera-${data.camera_id}-status`);
        if (statusElement) {
            statusElement.className = `badge bg-${this.getStatusColor(data.status)}`;
            statusElement.textContent = data.status;
        }

        // Show notification
        this.showNotification('Camera Update', `Camera ${data.camera_name} status changed to ${data.status}`);
    }

    handleNewIncident(data) {
        // Add incident to list if on incidents page
        const incidentsList = document.querySelector('#incidents-list');
        if (incidentsList) {
            const incidentHtml = this.createIncidentHtml(data);
            incidentsList.insertAdjacentHTML('afterbegin', incidentHtml);
        }

        // Show notification
        this.showNotification('New Incident', 
            `${data.title} reported at ${data.location}`, 
            data.priority === 'high' ? 'danger' : 'warning'
        );
    }

    handleMotionDetection(data) {
        // Update camera feed interface if on camera detail page
        const cameraFeed = document.querySelector(`#camera-${data.camera_id}-feed`);
        if (cameraFeed) {
            const alertHtml = `
                <div class="alert alert-warning alert-dismissible fade show" role="alert">
                    Motion detected at ${new Date(data.timestamp).toLocaleTimeString()}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `;
            cameraFeed.insertAdjacentHTML('beforebegin', alertHtml);
        }

        // Show notification
        this.showNotification('Motion Detected', 
            `Motion detected on camera ${data.camera_name} at ${data.location}`,
            'warning'
        );
    }

    showNotification(title, message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <strong>${title}</strong><br>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        const toastContainer = document.querySelector('.toast-container');
        if (toastContainer) {
            toastContainer.appendChild(toast);
            const bsToast = new bootstrap.Toast(toast);
            bsToast.show();
        }
    }

    getStatusColor(status) {
        switch(status) {
            case 'active':
                return 'success';
            case 'inactive':
                return 'danger';
            case 'maintenance':
                return 'warning text-dark';
            default:
                return 'secondary';
        }
    }

    createIncidentHtml(data) {
        return `
            <div class="list-group-item" id="incident-${data.incident_id}">
                <div class="d-flex w-100 justify-content-between">
                    <h5 class="mb-1">${data.title}</h5>
                    <small class="text-muted">Just now</small>
                </div>
                <p class="mb-1">Location: ${data.location}</p>
                <div>
                    <span class="badge bg-${data.priority === 'high' ? 'danger' : 'warning text-dark'}">
                        ${data.priority}
                    </span>
                    <small class="text-muted">Reported by ${data.reported_by}</small>
                </div>
            </div>
        `;
    }
}

class CameraWebSocket {
    constructor(cameraId) {
        this.cameraId = cameraId;
        this.connect();
    }

    connect() {
        // Use port 8001 for WebSocket connections
        const wsHost = window.location.hostname + ':8001';
        this.ws = new WebSocket(`ws://${wsHost}/ws/cameras/${this.cameraId}/`);
        this.ws.onmessage = (e) => this.onMessage(e);
    }

    onMessage(e) {
        const data = JSON.parse(e.data);
        if (data.message_type === 'motion_detected') {
            this.handleMotionDetection(data);
        }
    }

    handleMotionDetection(data) {
        const alertHtml = `
            <div class="alert alert-warning alert-dismissible fade show" role="alert">
                Motion detected at ${new Date(data.timestamp).toLocaleTimeString()}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        const alertsContainer = document.querySelector('#camera-alerts');
        if (alertsContainer) {
            alertsContainer.insertAdjacentHTML('afterbegin', alertHtml);
        }
    }
}
