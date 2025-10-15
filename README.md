# HELBPlace

A collaborative pixel-art web application inspired by Reddit’s r/place.  
Built as part of a university project at HELB using Django.

## Overview
HELBPlace allows users to create and manage collaborative pixel canvases where each participant can modify pixels in real time under a rate limit.  
It includes user authentication, profile management, statistics per canvas, and contributor rankings.

## Features
- User authentication and profile system
- Custom canvas creation with configurable size and pixel delay
- Real-time collaborative pixel editing (rate-limited)
- Canvas statistics and user ranking
- Administrative features and access control

## Technologies
- Django (Backend)
- HTML, CSS, JavaScript (Frontend)
- SQLite (default) or PostgreSQL
- Python 3.11+

## Installation
1. Clone the repository or download it.
2. Open a terminal in the project directory.
3. Run the following commands:
   ```bash
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver
