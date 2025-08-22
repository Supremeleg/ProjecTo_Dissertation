# -*- coding: utf-8 -*-
"""
ProjecTo Application Configuration Settings
Contains all constants, paths and configuration parameters
"""

import os
from pathlib import Path

class AppSettings:
    """Application settings class"""
    
    # ==================== Basic Path Configuration ====================
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    ASSETS_ROOT = PROJECT_ROOT / "assets"
    CONFIG_ROOT = PROJECT_ROOT / "config"
    
    # ==================== Display Configuration ====================
    # Fullscreen resolution
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    
    # Whether application is fullscreen
    FULLSCREEN = True
    
    # Background color (black)
    BACKGROUND_COLOR = "#000000"
    
    # ==================== Video Configuration ====================
    # Video file paths
    VIDEO_STAY = ASSETS_ROOT / "videos" / "stay.mp4"
    VIDEO_STAY2 = ASSETS_ROOT / "videos" / "stay2.mp4"  # Dedicated for REST stage
    VIDEO_GO_OUT = ASSETS_ROOT / "videos" / "go_out.mp4"
    VIDEO_GO_LEFT = ASSETS_ROOT / "videos" / "go_left.mp4"
    VIDEO_GO_RIGHT = ASSETS_ROOT / "videos" / "go_right.mp4"
    
    # Video rotation angle (clockwise 90°, use -90 in OpenCV)
    VIDEO_ROTATION_DEGREES = -90
    
    # Animation module size (relative to screen height)
    ANIMATION_SIZE_RATIO = 1/3  # One third of screen height
    
    # Animation movement speed
    ANIMATION_MOVE_DURATION = 2.0  # 2 seconds
    ANIMATION_PLAYBACK_SPEED = 4.0  # 4x playback speed during movement
    
    # ==================== Gesture Recognition Configuration ====================
    # Camera configuration
    CAMERA_INDEX = 0  # USB camera index
    CAMERA_WIDTH = 320          # Reduce resolution for better performance
    CAMERA_HEIGHT = 240         # Reduce resolution for better performance
    CAMERA_FPS = 30
    
    # Gesture detection distance range (centimeters)
    GESTURE_MIN_DISTANCE = 15   # Minimum 15cm
    GESTURE_MAX_DISTANCE = 80   # Maximum 80cm
    
    # Gesture recognition parameters
    GESTURE_DETECTION_CONFIDENCE = 0.7
    GESTURE_TRACKING_CONFIDENCE = 0.5
    
    # Wave detection parameters
    WAVE_AMPLITUDE_CM = 20  # Wave amplitude 20cm
    WAVE_MIN_FRAMES = 10    # Minimum detection frames
    
    # Long press gesture detection parameters
    LONG_PRESS_DURATION = 1.5          # Long press duration (seconds)
    LONG_PRESS_POSITION_THRESHOLD = 50 # Long press position stability threshold (pixels)
    LONG_PRESS_COOLDOWN = 3.0          # Long press detection cooldown time (seconds)
    
    # Double finger tap detection parameters
    DOUBLE_TAP_MAX_INTERVAL = 0.5      # Double finger tap maximum interval (seconds)
    DOUBLE_TAP_FINGER_DISTANCE = 50    # Double finger distance threshold (pixels)
    DOUBLE_TAP_POSITION_DRIFT = 60     # Position drift threshold (pixels)
    DOUBLE_TAP_COOLDOWN = 1.0          # Double finger tap cooldown time (seconds)
    
    # ==================== UI Configuration ====================
    # Theme colors
    PRIMARY_COLOR = "#FFFFFF"        # White
    SECONDARY_COLOR = "#808080"      # Gray
    ACCENT_COLOR_1 = "#00FFFF"       # Cyan
    ACCENT_COLOR_2 = "#FF0000"       # Red
    ACCENT_COLOR_3 = "#FFA500"       # Orange
    
    # Button configuration
    BUTTON_PRESSED_COLOR = "#FF0000"  # Red color when pressed
    BUTTON_GRADIENT_STOPS = [
        (0.0, "transparent"),
        (1.0, PRIMARY_COLOR)
    ]
    
    # Circular menu configuration
    MENU_BUTTON_COUNT = 4
    MENU_BUTTON_POSITIONS = ["top", "right", "bottom", "left"]  # Top, right, bottom, left
    MENU_RADIUS = 150  # Circle radius
    
    # Radial gradient button animation configuration
    RADIAL_ANIMATION_DURATION = 1.5  # Gradient animation duration
    
    # ==================== Stage Configuration ====================
    class Stage:
        """Stage configuration"""
        REST = "rest"
        PRIMARY_INTERACTION = "primary_interaction"  
        MENU_DETAIL = "menu_detail"
        OBJECT_RECOGNITION = "object_recognition"  # Object recognition
        SMART_CONTROL = "smart_control"            # Smart control
        TRACKING_MODE = "tracking_mode"            # Tracking mode
        GAME_MODE = "game_mode"                    # Game
        KEYBOARD_INPUT = "keyboard_input"          # Keyboard input

    # Default starting stage
    DEFAULT_STAGE = Stage.REST
    
    # ==================== Debug Configuration ====================
    DEBUG_MODE = False  # Whether to show debug information
    SHOW_CAMERA_WINDOW = True   # Whether to show camera window
    
    # ==================== Runtime Mode Configuration ====================
    MINIMAL_MODE = False  # Minimal mode: no stage prompts, no camera GUI, no keyboard control
    
    # ==================== Robotic Arm Configuration ====================
    ENABLE_ROBOT = False  # Whether to enable robotic arm (default off, requires hardware and LeRobot)
    
    # ==================== Subsystem Configuration ====================
    class SubSystem:
        """Subsystem enumeration"""
        SMART_HOME = "smart_home"        # Smart home control
        GAMES = "games"                  # Games
        OBJECT_RECOGNITION = "object_recognition"  # Object recognition
        FREE_TRACKING = "free_tracking"  # Free tracking
    
    # Subsystem display names
    SUBSYSTEM_NAMES = {
        SubSystem.SMART_HOME: "Smart Home",
        SubSystem.GAMES: "Games",
        SubSystem.OBJECT_RECOGNITION: "Object Recognition", 
        SubSystem.FREE_TRACKING: "Free Tracking"
    }
    
    # ==================== Robot Position Configuration ====================
    # Robot positions
    class RobotPosition:
        """Robot position enumeration"""
        REST = "rest"           # Rest position
        V_POSITION = "V"        # V position
        TRACKING = "tracking"   # Tracking position
    
    # Robot port configuration (requires hardware support)
    ROBOT_FOLLOWER_PORT = 'COM4'
    SERVO_PORT = 'COM3'
    SERVO_BAUDRATE = 9600
    
    # ==================== Logging Configuration ====================
    LOG_LEVEL = "INFO"  # Log level
    SHOW_FPS = False    # Whether to show FPS
    
    # ==================== Performance Configuration ====================
    # Vision processing optimization
    VISION_SKIP_FRAMES = 2      # Skip frame processing, process 1 frame every 3 frames
    VISION_RESIZE_FACTOR = 0.5  # Image scaling factor
    
    # Gesture detection optimization
    GESTURE_PROCESS_INTERVAL = 50  # Gesture processing interval (milliseconds)
    
    @classmethod
    def validate_paths(cls):
        """Validate whether paths exist"""
        print("Validating configuration paths...")
        
        # Check and create assets directory
        if not cls.ASSETS_ROOT.exists():
            print(f"Creating assets directory: {cls.ASSETS_ROOT}")
            cls.ASSETS_ROOT.mkdir(parents=True, exist_ok=True)
            (cls.ASSETS_ROOT / "videos").mkdir(exist_ok=True)
            (cls.ASSETS_ROOT / "images").mkdir(exist_ok=True)
            (cls.ASSETS_ROOT / "models").mkdir(exist_ok=True)
            
        # Check video files
        video_files = [
            cls.VIDEO_STAY,
            cls.VIDEO_STAY2,
            cls.VIDEO_GO_OUT, 
            cls.VIDEO_GO_LEFT,
            cls.VIDEO_GO_RIGHT
        ]
        
        missing_files = []
        for video_file in video_files:
            if not video_file.exists():
                missing_files.append(video_file.name)
        
        if missing_files:
            print(f"Note: Missing video files (system will use default display): {missing_files}")
            
        print("Configuration path validation complete")
        return True
    
    @classmethod
    def get_video_path(cls, video_name):
        """Get video file path"""
        video_map = {
            "stay": cls.VIDEO_STAY,
            "stay2": cls.VIDEO_STAY2,  # Dedicated for REST stage
            "go_out": cls.VIDEO_GO_OUT,
            "go_left": cls.VIDEO_GO_LEFT,
            "go_right": cls.VIDEO_GO_RIGHT
        }
        return video_map.get(video_name)
    
    @classmethod
    def setup_directories(cls):
        """Setup necessary directory structure"""
        directories = [
            cls.ASSETS_ROOT,
            cls.ASSETS_ROOT / "videos",
            cls.ASSETS_ROOT / "images", 
            cls.ASSETS_ROOT / "models",
            cls.CONFIG_ROOT,
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        print("Directory structure setup complete")
    
    @classmethod
    def print_config_summary(cls):
        """Print configuration summary"""
        print("=== ProjecTo Configuration Summary ===")
        print(f"Resolution: {cls.SCREEN_WIDTH}x{cls.SCREEN_HEIGHT}")
        print(f"Fullscreen mode: {cls.FULLSCREEN}")
        print(f"Camera: USB {cls.CAMERA_WIDTH}x{cls.CAMERA_HEIGHT}")
        print(f"Long press duration: {cls.LONG_PRESS_DURATION} seconds")
        print(f"Animation move duration: {cls.ANIMATION_MOVE_DURATION} seconds")
        print(f"Show camera window: {cls.SHOW_CAMERA_WINDOW}")
        print(f"Enable robot: {cls.ENABLE_ROBOT}")
        print(f"Debug mode: {cls.DEBUG_MODE}")
        print("=" * 40)
