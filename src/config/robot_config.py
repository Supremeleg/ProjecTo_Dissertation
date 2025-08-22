# -*- coding: utf-8 -*-
"""
Robotic Arm Configuration Module
Robotic arm configuration based on LeRobot framework, supporting optional dependencies
"""

import json
from pathlib import Path
from typing import Dict, Optional

class RobotConfig:
    """Robotic arm configuration class"""
    
    # ==================== Port Configuration ====================
    DEFAULT_FOLLOWER_PORT = 'COM4'
    DEFAULT_SERVO_PORT = 'COM3'
    DEFAULT_SERVO_BAUDRATE = 9600
    
    # ==================== Connection Configuration ====================
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_RETRY_DELAY = 2
    DEFAULT_CONNECTION_TIMEOUT = 5
    
    # ==================== Torque Configuration ====================
    DEFAULT_TORQUE_LIMITS = {
        "shoulder_pan": 300,
        "shoulder_lift": 400,
        "elbow_flex": 600,
        "wrist_flex": 300,
        "wrist_roll": 300
    }
    
    # ==================== 默认位置配置 ====================
    DEFAULT_POSITIONS = {
        "rest": {
            "shoulder_pan": 0,
            "shoulder_lift": -2048,
            "elbow_flex": 1024,
            "wrist_flex": 0,
            "wrist_roll": 0,
            "servo_angle": 90
        },
        "V": {
            "shoulder_pan": 0,
            "shoulder_lift": -1024,
            "elbow_flex": 2048,
            "wrist_flex": -1024,
            "wrist_roll": 0,
            "servo_angle": 90
        },
        "tracking": {
            "shoulder_pan": 0,
            "shoulder_lift": -512,
            "elbow_flex": 1536,
            "wrist_flex": -512,
            "wrist_roll": 0,
            "servo_angle": 90
        }
    }
    
    # ==================== 动作配置 ====================
    DEFAULT_MOVEMENT_STEPS = 30  # 分步移动的步数
    DEFAULT_STEP_DELAY = 0.06    # 每步之间的延迟（秒）
    DEFAULT_THRESHOLD = 11.4
    
    def __init__(self, config_file: Optional[Path] = None):
        """初始化机械臂配置"""
        self.config_file = config_file or (
            Path(__file__).parent.parent.parent / "config" / "robot_config.json"
        )
        
        # 初始化配置
        self.follower_port = self.DEFAULT_FOLLOWER_PORT
        self.servo_port = self.DEFAULT_SERVO_PORT
        self.servo_baudrate = self.DEFAULT_SERVO_BAUDRATE
        self.max_retries = self.DEFAULT_MAX_RETRIES
        self.retry_delay = self.DEFAULT_RETRY_DELAY
        self.connection_timeout = self.DEFAULT_CONNECTION_TIMEOUT
        self.torque_limits = self.DEFAULT_TORQUE_LIMITS.copy()
        self.positions = self.DEFAULT_POSITIONS.copy()
        self.movement_steps = self.DEFAULT_MOVEMENT_STEPS
        self.step_delay = self.DEFAULT_STEP_DELAY
        self.threshold = self.DEFAULT_THRESHOLD
        
        # 位置文件路径
        self.positions_root = Path(__file__).parent.parent.parent
        self.position_files = {
            "rest": self.positions_root / "config" / "positions" / "rest_positions.json",
            "tracking": self.positions_root / "config" / "positions" / "tracking_positions.json",
            "vertical": self.positions_root / "config" / "positions" / "vertical_positions.json"
        }
        
        # 加载配置
        self.load_config()
        
    def load_config(self):
        """从文件加载配置"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    self._update_from_dict(config_data)
                print(f"机械臂配置已加载: {self.config_file}")
            else:
                print(f"机械臂配置文件不存在，使用默认配置: {self.config_file}")
                self.save_config()
        except Exception as e:
            print(f"加载机械臂配置失败，使用默认配置: {e}")
    
    def save_config(self):
        """保存配置到文件"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            config_data = self._to_dict()
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            print(f"机械臂配置已保存: {self.config_file}")
        except Exception as e:
            print(f"保存机械臂配置失败: {e}")
    
    def _update_from_dict(self, config_data: Dict):
        """从字典更新配置"""
        self.follower_port = config_data.get("follower_port", self.follower_port)
        self.servo_port = config_data.get("servo_port", self.servo_port)
        self.servo_baudrate = config_data.get("servo_baudrate", self.servo_baudrate)
        self.max_retries = config_data.get("max_retries", self.max_retries)
        self.retry_delay = config_data.get("retry_delay", self.retry_delay)
        self.connection_timeout = config_data.get("connection_timeout", self.connection_timeout)
        
        if "torque_limits" in config_data:
            self.torque_limits.update(config_data["torque_limits"])
        
        if "positions" in config_data:
            self.positions.update(config_data["positions"])
            
        self.movement_steps = config_data.get("movement_steps", self.movement_steps)
        self.step_delay = config_data.get("step_delay", self.step_delay)
        self.threshold = config_data.get("threshold", self.threshold)
    
    def _to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "follower_port": self.follower_port,
            "servo_port": self.servo_port,
            "servo_baudrate": self.servo_baudrate,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "connection_timeout": self.connection_timeout,
            "torque_limits": self.torque_limits,
            "positions": self.positions,
            "movement_steps": self.movement_steps,
            "step_delay": self.step_delay,
            "threshold": self.threshold,
        }
    
    def get_position(self, position_name: str) -> Optional[Dict]:
        """获取指定位置配置"""
        return self.positions.get(position_name)
    
    def set_position(self, position_name: str, position_data: Dict):
        """设置位置配置"""
        self.positions[position_name] = position_data
    
    def load_position_from_file(self, position_name: str) -> Optional[Dict]:
        """从文件加载位置配置"""
        position_file = self.position_files.get(position_name)
        if not position_file or not position_file.exists():
            return None
        
        try:
            with open(position_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载位置文件失败 {position_file}: {e}")
            return None
    
    def save_position_to_file(self, position_name: str, position_data: Dict):
        """保存位置配置到文件"""
        position_file = self.position_files.get(position_name)
        if not position_file:
            return False
        
        try:
            position_file.parent.mkdir(parents=True, exist_ok=True)
            with open(position_file, 'w', encoding='utf-8') as f:
                json.dump(position_data, f, indent=2, ensure_ascii=False)
            print(f"位置配置已保存: {position_file}")
            return True
        except Exception as e:
            print(f"保存位置文件失败 {position_file}: {e}")
            return False
    
    def get_lerobot_config(self):
        """获取LeRobot兼容的配置（如果安装了LeRobot）"""
        try:
            from lerobot.common.robot_devices.robots.configs import So101RobotConfig
            
            # 创建LeRobot配置
            lerobot_config = So101RobotConfig()
            
            # 移除Leader臂配置（仅使用Follower）
            lerobot_config.leader_arms = {}
            
            # 配置Follower臂端口
            for arm_name in lerobot_config.follower_arms:
                lerobot_config.follower_arms[arm_name].port = self.follower_port
                
                # 移除gripper配置（如果不需要）
                if "gripper" in lerobot_config.follower_arms[arm_name].motors:
                    del lerobot_config.follower_arms[arm_name].motors["gripper"]
            
            # 禁用摄像头（使用自己的摄像头管理）
            lerobot_config.cameras = {}
            
            return lerobot_config
            
        except ImportError:
            print("LeRobot未安装，无法创建LeRobot配置")
            return None
    
    def print_config(self):
        """打印配置信息"""
        print("=== 机械臂配置 ===")
        print(f"Follower端口: {self.follower_port}")
        print(f"舵机端口: {self.servo_port}")
        print(f"舵机波特率: {self.servo_baudrate}")
        print(f"最大重试次数: {self.max_retries}")
        print(f"连接超时: {self.connection_timeout}秒")
        print(f"移动步数: {self.movement_steps}")
        print(f"步长延迟: {self.step_delay}秒")
        print("扭矩限制:", self.torque_limits)
        print("预设位置:", list(self.positions.keys()))
        print("================")
