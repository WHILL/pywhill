#!/usr/bin/env python3
"""
WHILL API Server

A RESTful API server for controlling WHILL mobility devices.
This example demonstrates how to use the pywhill library to create 
a web API for WHILL control and monitoring.

Author: WHILL, Inc.
License: MIT License
Repository: https://github.com/WHILL/pywhill/tree/master/example/webapi

Dependencies:
- pywhill: WHILL control library
- Flask: Web framework
- flasgger: Swagger documentation
- waitress: WSGI server for production

Usage:
    Development: python app.py
    Production: Set WHILL_API_ENV=production and run
"""

import os
import threading
import logging
from datetime import datetime

from whill import ComWHILL
from flask import Flask, jsonify, request
from flasgger import Swagger
from waitress import serve

app = Flask(__name__)
swagger = Swagger(app)

# Environment configuration
ENVIRONMENT = os.environ.get('WHILL_API_ENV', 'development')
HOST = os.environ.get('WHILL_API_HOST', '0.0.0.0')
PORT = int(os.environ.get('WHILL_API_PORT', '5000'))
THREADS = int(os.environ.get('WHILL_API_THREADS', '4'))

# WHILL connection settings (from environment variables, default is /dev/ttyUSB0)
WHILL_PORT = os.environ.get('WHILL_PORT', '/dev/ttyUSB0')
WHILL_TIMEOUT = float(os.environ.get('WHILL_TIMEOUT', '1.0'))

# Logging configuration
if ENVIRONMENT == 'production':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s %(message)s',
        handlers=[
            logging.FileHandler('app.log'),
            logging.StreamHandler()
        ]
    )
else:
    logging.basicConfig(level=logging.DEBUG)

# WHILL instance (global)
whill = None
whill_lock = threading.Lock()

def get_whill_instance():
    """Get WHILL instance (including initialization)"""
    global whill
    if whill is None:
        try:
            whill = ComWHILL(port=WHILL_PORT, timeout=WHILL_TIMEOUT)
        except Exception as e:
            raise Exception(f"Failed to connect to WHILL: {str(e)}")
    return whill

def create_error_response(message, code=400):
    """Generate error response"""
    return jsonify({
        'success': False,
        'error': message,
        'timestamp': datetime.now().isoformat()
    }), code

def create_success_response(data=None, message="Operation completed successfully"):
    """Generate success response"""
    response = {
        'success': True,
        'message': message,
        'timestamp': datetime.now().isoformat()
    }
    if data is not None:
        response['data'] = data
    return jsonify(response)

# =============================================================================
# WHILL Power Control APIs
# =============================================================================

@app.route('/api/v1/whill/power', methods=['POST'])
def control_power():
    """
    Power control
    ---
    tags:
      - WHILL Power Control
    summary: Power control
    description: Turn WHILL power ON/OFF
    parameters:
      - in: body
        name: body
        description: Power control parameters
        required: true
        schema:
          type: object
          properties:
            power_on:
              type: boolean
              description: Power state (true=ON, false=OFF)
              example: true
          required:
            - power_on
    responses:
      200:
        description: Control successful
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Power turned ON"
            data:
              type: object
              properties:
                power_on:
                  type: boolean
            timestamp:
              type: string
              format: date-time
      400:
        description: Parameter error
      500:
        description: Server error
    """
    try:
        data = request.get_json()
        if not data:
            return create_error_response("JSON data is required")
        
        power_on = data.get('power_on')
        if power_on is None:
            return create_error_response("power_on parameter is required")
        
        if not isinstance(power_on, bool):
            return create_error_response("power_on must be a boolean value")
        
        with whill_lock:
            whill_instance = get_whill_instance()
            whill_instance.set_power(power_on)
        
        return create_success_response({
            'power_on': power_on
        }, f"Power turned {'ON' if power_on else 'OFF'}")
        
    except Exception as e:
        return create_error_response(f"Power control error: {str(e)}", 500)

# =============================================================================
# WHILL Motion Control APIs
# =============================================================================

@app.route('/api/v1/whill/motion/joystick', methods=['POST'])
def control_joystick():
    """
    Joystick control
    ---
    tags:
      - WHILL Motion Control
    summary: Joystick control
    description: Controls WHILL's joystick. You can select single shot or hold control based on the timeout parameter.
    parameters:
      - in: body
        name: body
        description: Joystick control parameters
        required: true
        schema:
          type: object
          properties:
            front:
              type: number
              description: Control value for front-back direction (-100 to 100)
              minimum: -100
              maximum: 100
              example: 50
            side:
              type: number
              description: Control value for left-right direction (-100 to 100)
              minimum: -100
              maximum: 100
              example: 0
            timeout:
              type: number
              description: Duration in milliseconds. If not specified or 0, it's single shot control, otherwise it's hold control (max 60000).
              minimum: 0
              maximum: 60000
              example: 1000
          required:
            - front
            - side
    responses:
      200:
        description: Control successful
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Joystick control command sent"
            data:
              type: object
              properties:
                front:
                  type: number
                side:
                  type: number
                timeout:
                  type: number
                control_type:
                  type: string
                  description: Control type (single_shot or hold)
            timestamp:
              type: string
              format: date-time
      400:
        description: Parameter error
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
            timestamp:
              type: string
              format: date-time
      500:
        description: Server error
    """
    try:
        data = request.get_json()
        if not data:
            return create_error_response("JSON data is required")
        
        front = data.get('front', 0)
        side = data.get('side', 0)
        timeout = data.get('timeout', 0)
        
        # Parameter validation
        if not isinstance(front, (int, float)) or not isinstance(side, (int, float)):
            return create_error_response("front and side must be numeric values")
        
        if not isinstance(timeout, (int, float)) or timeout < 0:
            return create_error_response("timeout must be a non-negative numeric value")
        
        if not (-100 <= front <= 100) or not (-100 <= side <= 100):
            return create_error_response("front and side must be in the range of -100 to 100")
        
        with whill_lock:
            whill_instance = get_whill_instance()
            
            if timeout == 0:
                # Single shot control
                whill_instance.send_joystick(int(front), int(side))
                control_type = "single_shot"
                message = "Joystick control command sent"
            else:
                # Hold control
                whill_instance.hold_joy(int(front), int(side), int(timeout))
                control_type = "hold"
                message = "Joystick hold control started"
        
        return create_success_response({
            'front': front,
            'side': side,
            'timeout': timeout,
            'control_type': control_type
        }, message)
        
    except Exception as e:
        return create_error_response(f"Joystick control error: {str(e)}", 500)

@app.route('/api/v1/whill/motion/velocity', methods=['POST'])
def control_velocity():
    """
    Velocity control
    ---
    tags:
      - WHILL Motion Control
    summary: Velocity control
    description: Controls WHILL's velocity. You can select single shot or hold control based on the timeout parameter.
    parameters:
      - in: body
        name: body
        description: Velocity control parameters
        required: true
        schema:
          type: object
          properties:
            front:
              type: number
              description: Velocity value for front-back direction (-500 to 1500)
              minimum: -500
              maximum: 1500
              example: 1000
            side:
              type: number
              description: Velocity value for left-right direction (-750 to 750)
              minimum: -750
              maximum: 750
              example: 0
            timeout:
              type: number
              description: Duration in milliseconds. If not specified or 0, it's single shot control, otherwise it's hold control (max 60000).
              minimum: 0
              maximum: 60000
              example: 1000
          required:
            - front
            - side
    responses:
      200:
        description: Control successful
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Velocity control command sent"
            data:
              type: object
              properties:
                front:
                  type: number
                side:
                  type: number
                timeout:
                  type: number
                control_type:
                  type: string
                  description: Control type (single_shot or hold)
            timestamp:
              type: string
              format: date-time
      400:
        description: Parameter error
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
            timestamp:
              type: string
              format: date-time
      500:
        description: Server error
    """
    try:
        data = request.get_json()
        if not data:
            return create_error_response("JSON data is required")
        
        front = data.get('front', 0)
        side = data.get('side', 0)
        timeout = data.get('timeout', 0)
        
        # Parameter validation
        if not isinstance(front, (int, float)) or not isinstance(side, (int, float)):
            return create_error_response("front and side must be numeric values")
        
        if not isinstance(timeout, (int, float)) or timeout < 0:
            return create_error_response("timeout must be a non-negative numeric value")
        
        if not (-500 <= front <= 1500) or not (-750 <= side <= 750):
            return create_error_response("front and side must be in the range of -500 to 1500 and -750 to 750")
        
        with whill_lock:
            whill_instance = get_whill_instance()
            
            if timeout == 0:
                # Single shot control
                whill_instance.send_velocity(int(front), int(side))
                control_type = "single_shot"
                message = "Velocity control command sent"
            else:
                # Hold control
                whill_instance.hold_velocity(int(front), int(side), int(timeout))
                control_type = "hold"
                message = "Velocity hold control started"
        
        return create_success_response({
            'front': front,
            'side': side,
            'timeout': timeout,
            'control_type': control_type
        }, message)
        
    except Exception as e:
        return create_error_response(f"Velocity control error: {str(e)}", 500)

@app.route('/api/v1/whill/motion/release', methods=['POST'])
def release_control():
    """
    Control release
    ---
    tags:
      - WHILL Motion Control
    summary: Control release
    description: Release active joystick or velocity hold control
    responses:
      200:
        description: Control release successful
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Control released"
            data:
              type: object
              properties:
                released_control_type:
                  type: string
                  description: Released control type (joystick, velocity, or none)
                  example: "joystick"
            timestamp:
              type: string
              format: date-time
      500:
        description: Server error
    """
    try:
        with whill_lock:
            whill_instance = get_whill_instance()
            
            # Get current active control type
            current_control_type = getattr(whill_instance, '_ComWHILL__hold_control_type', None)
            
            # Release hold control
            whill_instance.unhold()
            
            # Determine released control type
            if current_control_type == 'joy':
                released_type = 'joystick'
                message = "Joystick control released"
            elif current_control_type == 'velocity':
                released_type = 'velocity'
                message = "Velocity control released"
            else:
                released_type = 'none'
                message = "No control was active"
        
        return create_success_response({
            'released_control_type': released_type
        }, message)
        
    except Exception as e:
        return create_error_response(f"Control release error: {str(e)}", 500)

# =============================================================================
# WHILL Data Stream APIs
# =============================================================================

@app.route('/api/v1/whill/data-streams/start', methods=['POST'])
def start_data_stream():
    """
    Start data stream
    ---
    tags:
      - WHILL Data Stream
    summary: Start data stream
    description: Start data stream from WHILL
    parameters:
      - in: body
        name: body
        description: Data stream start parameters
        required: true
        schema:
          type: object
          properties:
            interval_msec:
              type: integer
              description: Data transmission interval in milliseconds (10-65535)
              minimum: 10
              maximum: 65535
              default: 1000
              example: 1000
            data_set_number:
              type: integer
              description: Data set number (0 or 1)
              enum: [0, 1]
              default: 1
              example: 1
            speed_mode:
              type: integer
              description: Speed mode setting (0-5) only data_set_number=0 is valid
              minimum: 0
              maximum: 5
              default: 4
              example: 4
    responses:
      200:
        description: Data stream started successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Data stream started"
            data:
              type: object
              properties:
                interval_msec:
                  type: integer
                data_set_number:
                  type: integer
                speed_mode:
                  type: integer
            timestamp:
              type: string
              format: date-time
      400:
        description: Parameter error
      500:
        description: Server error
    """
    try:
        data = request.get_json()
        if not data:
            return create_error_response("JSON data is required")
        
        interval_msec = data.get('interval_msec', 1000)
        data_set_number = data.get('data_set_number', 1)
        speed_mode = data.get('speed_mode', 4)
        
        # Parameter validation
        if not isinstance(interval_msec, int) or interval_msec < 10:
            return create_error_response("interval_msec must be a positive integer")
        
        if not isinstance(data_set_number, int) or data_set_number not in [0, 1]:
            return create_error_response("data_set_number must be 0 or 1")
        
        if not isinstance(speed_mode, int) or not (0 <= speed_mode <= 5):
            return create_error_response("speed_mode must be in the range of 0 to 5")
        
        with whill_lock:
            whill_instance = get_whill_instance()
            whill_instance.start_data_stream(interval_msec, data_set_number, speed_mode)
        
        return create_success_response({
            'interval_msec': interval_msec,
            'data_set_number': data_set_number,
            'speed_mode': speed_mode
        }, "Data stream started")
        
    except Exception as e:
        return create_error_response(f"Data stream start error: {str(e)}", 500)

@app.route('/api/v1/whill/data-streams/stop', methods=['POST'])
def stop_data_stream():
    """
    Stop data stream
    ---
    tags:
      - WHILL Data Stream
    summary: Stop data stream
    description: Stop active data stream
    responses:
      200:
        description: Data stream stopped successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Data stream stopped"
            timestamp:
              type: string
              format: date-time
      500:
        description: Server error
    """
    try:
        with whill_lock:
            whill_instance = get_whill_instance()
            whill_instance.stop_data_stream()
        
        return create_success_response(message="Data stream stopped")
        
    except Exception as e:
        return create_error_response(f"Data stream stop error: {str(e)}", 500)

# =============================================================================
# WHILL Status APIs
# =============================================================================

@app.route('/api/v1/whill/status', methods=['GET'])
def get_whill_status():
    """
    Get WHILL comprehensive status
    ---
    tags:
      - WHILL Status
    summary: Get WHILL comprehensive status
    description: Retrieve comprehensive status information of WHILL including basic status, battery, and motor information
    responses:
      200:
        description: Comprehensive status acquisition successful
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Comprehensive status retrieved"
            data:
              type: object
              properties:
                basic_status:
                  type: object
                  description: Basic WHILL status information
                  properties:
                    power_status:
                      type: integer
                      description: Power status
                    speed_mode_indicator:
                      type: integer
                      description: Speed mode indicator
                    error_code:
                      type: integer
                      description: Error code
                battery:
                  type: object
                  description: Battery information including charge level, voltage, etc.
                motors:
                  type: object
                  description: Motor information for both left and right motors
                  properties:
                    right_motor:
                      type: object
                      description: Right motor information including angle, speed, etc.
                    left_motor:
                      type: object
                      description: Left motor information including angle, speed, etc.
            timestamp:
              type: string
              format: date-time
      500:
        description: Server error
    """
    try:
        with whill_lock:
            whill_instance = get_whill_instance()
            whill_instance.refresh()
            
            # Comprehensive status including basic status, battery, and motors
            comprehensive_status = {
                'basic_status': {
                    'power_status': whill_instance.power_status,
                    'speed_mode_indicator': whill_instance.speed_mode_indicator,
                    'error_code': whill_instance.error_code
                },
                'battery': dict(whill_instance.battery),
                'motors': {
                    'right_motor': dict(whill_instance.right_motor),
                    'left_motor': dict(whill_instance.left_motor)
                }
            }
        
        return create_success_response(comprehensive_status, "Comprehensive status retrieved")
        
    except Exception as e:
        return create_error_response(f"Comprehensive status retrieval error: {str(e)}", 500)

@app.route('/api/v1/whill/battery', methods=['GET'])
def get_battery_info():
    """
    Get battery information
    ---
    tags:
      - WHILL Status
    summary: Get battery information
    description: Retrieve WHILL's battery information
    responses:
      200:
        description: Battery information acquisition successful
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Battery information retrieved"
            data:
              type: object
              description: Battery related information
            timestamp:
              type: string
              format: date-time
      500:
        description: Server error
    """
    try:
        with whill_lock:
            whill_instance = get_whill_instance()
            whill_instance.refresh()
            
            battery_info = dict(whill_instance.battery)
        
        return create_success_response(battery_info, "Battery information retrieved")
        
    except Exception as e:
        return create_error_response(f"Battery information retrieval error: {str(e)}", 500)

@app.route('/api/v1/whill/motors', methods=['GET'])
def get_motor_info():
    """
    Get motor information
    ---
    tags:
      - WHILL Status
    summary: Get motor information
    description: Retrieve WHILL's left and right motor information
    responses:
      200:
        description: Motor information acquisition successful
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Motor information retrieved"
            data:
              type: object
              properties:
                right_motor:
                  type: object
                  description: Right motor information
                left_motor:
                  type: object
                  description: Left motor information
            timestamp:
              type: string
              format: date-time
      500:
        description: Server error
    """
    try:
        with whill_lock:
            whill_instance = get_whill_instance()
            whill_instance.refresh()
            
            motor_info = {
                'right_motor': dict(whill_instance.right_motor),
                'left_motor': dict(whill_instance.left_motor)
            }
        
        return create_success_response(motor_info, "Motor information retrieved")
        
    except Exception as e:
        return create_error_response(f"Motor information retrieval error: {str(e)}", 500)

# =============================================================================
# WHILL Configuration APIs
# =============================================================================

@app.route('/api/v1/whill/speed-profiles', methods=['POST'])
def set_speed_profile():
    """
    Speed profile configuration
    ---
    tags:
      - WHILL Configuration
    summary: Speed profile configuration
    description: Configure WHILL's speed profile
    parameters:
      - in: body
        name: body
        description: Speed profile configuration parameters
        required: true
        schema:
          type: object
          properties:
            speed_mode:
              type: integer
              description: Speed mode to configure (0-5)
              minimum: 0
              maximum: 5
              example: 4
            profile:
              type: object
              description: Speed profile settings
              properties:
                forward_speed:
                  type: number
                  description: Maximum forward speed (8-60)
                  minimum: 8
                  maximum: 60
                  example: 60
                forward_acceleration:
                  type: number
                  description: Forward acceleration rate (10-64)
                  minimum: 10
                  maximum: 64
                  example: 56
                forward_deceleration:
                  type: number
                  description: Forward deceleration rate (40-160)
                  minimum: 40
                  maximum: 160
                  example: 125
                reverse_speed:
                  type: number
                  description: Maximum reverse speed (8-30)
                  minimum: 8
                  maximum: 30
                  example: 20
                reverse_acceleration:
                  type: number
                  description: Reverse acceleration rate (10-50)
                  minimum: 10
                  maximum: 50
                  example: 24
                reverse_deceleration:
                  type: number
                  description: Reverse deceleration rate (40-80)
                  minimum: 40
                  maximum: 80
                  example: 56
                turn_speed:
                  type: number
                  description: Maximum turning speed (8-35)
                  minimum: 8
                  maximum: 35
                  example: 25
                turn_acceleration:
                  type: number
                  description: Turning acceleration rate (10-60)
                  minimum: 10
                  maximum: 60
                  example: 56
                turn_deceleration:
                  type: number
                  description: Turning deceleration rate (40-160)
                  minimum: 40
                  maximum: 160
                  example: 72
              required:
                - forward_speed
                - forward_acceleration
                - forward_deceleration
                - reverse_speed
                - reverse_acceleration
                - reverse_deceleration
                - turn_speed
                - turn_acceleration
                - turn_deceleration
          required:
            - speed_mode
            - profile
    responses:
      200:
        description: Configuration successful
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Speed profile configured"
            data:
              type: object
              properties:
                speed_mode:
                  type: integer
                profile:
                  type: object
            timestamp:
              type: string
              format: date-time
      400:
        description: Parameter error
      500:
        description: Server error
    """
    try:
        data = request.get_json()
        if not data:
            return create_error_response("JSON data is required")
        
        speed_mode = data.get('speed_mode')
        profile = data.get('profile')
        
        if speed_mode is None or profile is None:
            return create_error_response("speed_mode and profile parameters are required")
        
        if not isinstance(speed_mode, int) or not (0 <= speed_mode <= 5):
            return create_error_response("speed_mode must be an integer between 0 and 5")
        
        # Profile item validation
        required_keys = ['forward_speed', 'forward_acceleration', 'forward_deceleration',
                        'reverse_speed', 'reverse_acceleration', 'reverse_deceleration',
                        'turn_speed', 'turn_acceleration', 'turn_deceleration']
        
        for key in required_keys:
            if key not in profile:
                return create_error_response(f"profile requires {key}")
            if not isinstance(profile[key], (int, float)):
                return create_error_response(f"profile.{key} must be a numeric value")
        
        with whill_lock:
            whill_instance = get_whill_instance()
            whill_instance.set_speed_profile_via_dict(speed_mode, profile)
        
        return create_success_response({
            'speed_mode': speed_mode,
            'profile': profile
        }, "Speed profile configured")
        
    except Exception as e:
        return create_error_response(f"Speed profile configuration error: {str(e)}", 500)

@app.route('/api/v1/whill/speed-profiles', methods=['GET'])
def get_speed_profiles():
    """
    Get speed profiles list
    ---
    tags:
      - WHILL Configuration
    summary: Get speed profiles list
    description: Retrieve all speed profiles configured on WHILL
    responses:
      200:
        description: Speed profiles acquisition successful
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Speed profiles retrieved"
            data:
              type: array
              items:
                type: object
                properties:
                  mode:
                    type: integer
                    description: Speed mode number
                  profile:
                    type: object
                    description: Speed profile settings
            timestamp:
              type: string
              format: date-time
      500:
        description: Server error
    """
    try:
        with whill_lock:
            whill_instance = get_whill_instance()
            whill_instance.refresh()
            
            profiles = []
            for i, profile in enumerate(whill_instance.speed_profile):
                profiles.append({
                    'mode': i,
                    'profile': dict(profile)
                })
        
        return create_success_response(profiles, "Speed profiles retrieved")
        
    except Exception as e:
        return create_error_response(f"Speed profile retrieval error: {str(e)}", 500)

@app.route('/api/v1/whill/battery/saving', methods=['POST'])
def set_battery_saving():
    """
    Battery saving configuration
    ---
    tags:
      - WHILL Configuration
    summary: Battery saving configuration
    description: Configure WHILL's battery saving settings
    parameters:
      - in: body
        name: body
        description: Battery saving configuration parameters
        required: false
        schema:
          type: object
          properties:
            low_battery_level:
              type: integer
              description: Battery level threshold for saving mode (1-90)
              minimum: 1
              maximum: 90
              default: 19
              example: 20
            sounds_buzzer:
              type: boolean
              description: Whether to sound buzzer when battery is low
              default: true
              example: true
    responses:
      200:
        description: Configuration successful
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Battery saving settings applied"
            data:
              type: object
              properties:
                low_battery_level:
                  type: integer
                sounds_buzzer:
                  type: boolean
            timestamp:
              type: string
              format: date-time
      400:
        description: Parameter error
      500:
        description: Server error
    """
    try:
        data = request.get_json() if request.get_json() else {}
        
        low_battery_level = data.get('low_battery_level', 19)
        sounds_buzzer = data.get('sounds_buzzer', True)
        
        # Parameter validation
        if not isinstance(low_battery_level, int):
            return create_error_response("low_battery_level must be an integer")
        
        if not (1 <= low_battery_level <= 90):
            return create_error_response("low_battery_level must be in the range of 1 to 90")
        
        if not isinstance(sounds_buzzer, bool):
            return create_error_response("sounds_buzzer must be a boolean value")
        
        with whill_lock:
            whill_instance = get_whill_instance()
            whill_instance.set_battery_saving(low_battery_level, sounds_buzzer)
        
        return create_success_response({
            'low_battery_level': low_battery_level,
            'sounds_buzzer': sounds_buzzer
        }, "Battery saving settings applied")
        
    except Exception as e:
        return create_error_response(f"Battery saving settings error: {str(e)}", 500)

# =============================================================================
# WHILL Diagnostics APIs
# =============================================================================

@app.route('/api/v1/whill/diagnostics/connection', methods=['GET'])
def test_connection():
    """
    WHILL connection test
    ---
    tags:
      - WHILL Diagnostics
    summary: WHILL connection test
    description: Test connection status with WHILL
    responses:
      200:
        description: Connection test completed
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Connection test completed"
            data:
              type: object
              properties:
                connected:
                  type: boolean
                  description: Connection status
                  example: true
                port:
                  type: string
                  description: Port in use
                  example: "COM3"
            timestamp:
              type: string
              format: date-time
      500:
        description: Server error
    """
    try:
        with whill_lock:
            whill_instance = get_whill_instance()
            # easy way to check if the connection is open
            is_connected = whill_instance.com.is_open if hasattr(whill_instance.com, 'is_open') else True
        
        return create_success_response({
            'connected': is_connected,
            'port': WHILL_PORT
        }, "Connection test completed")
        
    except Exception as e:
        return create_error_response(f"Connection test error: {str(e)}", 500)


if __name__ == '__main__':
    if ENVIRONMENT == 'production':
        # production environment: use Waitress
        print(f"Starting production server on {HOST}:{PORT}")
        print(f"WHILL Port: {WHILL_PORT}")
        print(f"Environment: {ENVIRONMENT}")
        serve(app, host=HOST, port=PORT, threads=THREADS)
    else:
        # development environment: use Flask's development server
        print(f"Starting development server on {HOST}:{PORT}")
        print(f"WHILL Port: {WHILL_PORT}")
        print(f"Environment: {ENVIRONMENT}")
        app.run(host=HOST, port=PORT, debug=True)
