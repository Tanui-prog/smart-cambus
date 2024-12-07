# Smart Campus Security System

A comprehensive security management platform with real-time monitoring and incident tracking capabilities. The system provides privacy-conscious surveillance, real-time motion detection, and incident management features.

## Features

- **Real-time Camera Monitoring**
  - Live video streaming with OpenCV integration
  - Motion detection with real-time alerts
  - Camera status tracking
  - Privacy-preserving design
  - Timestamp overlay on video feeds

- **Incident Management**
  - Real-time incident reporting
  - Priority-based classification
  - Incident tracking and updates
  - Evidence collection support
  - Comprehensive logging

- **User Management**
  - Role-based access control
  - Activity tracking
  - Granular permissions
  - Secure authentication

- **Real-time Notifications**
  - WebSocket-based updates
  - Motion detection alerts
  - Camera status changes
  - Incident reports
  - Access attempt logging

## Technical Architecture

- **Backend Framework**: Django 4.2.7
- **Real-time Communication**: Django Channels with Redis
- **Video Processing**: OpenCV
- **Frontend**: Bootstrap 5, Font Awesome
- **Database**: PostgreSQL (recommended)
- **Caching**: Redis

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd smart_campus
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up Redis:
- Install Redis server
- Ensure Redis is running on localhost:6379

5. Configure environment variables:
- Copy `.env.example` to `.env`
- Update the variables as needed

6. Initialize the database:
```bash
python manage.py migrate
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

## Configuration

### Camera Setup
- Configure camera sources in the admin interface
- Adjust motion detection sensitivity in settings
- Set up camera zones and access permissions

### Security Settings
- Configure SSL in production
- Set up proper authentication methods
- Review and adjust permission settings

### WebSocket Configuration
- Ensure Redis is properly configured
- Adjust WebSocket settings in settings.py
- Configure proper SSL for WebSocket in production

## Usage

### Camera Monitoring
1. Access the dashboard
2. Navigate to the Cameras section
3. Select a camera to view its live feed
4. Monitor motion detection alerts

### Incident Management
1. Create new incidents
2. Assign priority levels
3. Track and update status
4. Attach evidence and notes

### User Management
1. Create user accounts
2. Assign roles and permissions
3. Monitor user activity
4. Manage access controls

## Development

### Project Structure
```
smart_campus/
├── security/           # Camera and monitoring
├── incidents/          # Incident management
├── users/             # User management
├── static/            # Static files
│   ├── css/
│   └── js/
└── templates/         # HTML templates
```

### Key Components
- `security/consumers.py`: WebSocket consumers
- `security/views.py`: Camera monitoring views
- `security/utils.py`: Utility functions
- `incidents/models.py`: Incident data models
- `users/models.py`: Custom user model

## Production Deployment

### Requirements
- PostgreSQL database
- Redis server
- HTTPS certificate
- Proper server configuration

### Recommendations
1. Use HTTPS for all connections
2. Configure proper CORS settings
3. Use environment variables
4. Set DEBUG=False
5. Configure proper logging
6. Use a production-ready web server

## Security Considerations

- All camera feeds are encrypted
- Access logs are maintained
- Role-based access control
- Activity monitoring
- Secure WebSocket connections
- Privacy-preserving design

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
