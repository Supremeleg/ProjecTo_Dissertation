#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ProjecTo机械臂控制演示
展示如何使用集成的LeRobot功能控制SO101机械臂
"""

import sys
import time
import json
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QSlider, QTextEdit
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

# ProjecTo导入
from config.settings import AppSettings

# LeRobot集成导入
try:
    from lerobot_integration.robot_devices.robots.configs import (
        create_projecto_follower_only_config,
        create_projecto_so101_config
    )
    from lerobot_integration.robot_devices.robots.manipulator import ManipulatorRobot
    LEROBOT_INTEGRATION_AVAILABLE = True
except ImportError as e:
    print(f"LeRobot集成不可用: {e}")
    LEROBOT_INTEGRATION_AVAILABLE = False

class RobotControlDemo(QMainWindow):
    """机械臂控制演示窗口"""
    
    def __init__(self):
        super().__init__()
        self.robot = None
        self.robot_config = None
        self.is_connected = False
        
        # 位置存储
        self.saved_positions = {}
        self.load_saved_positions()
        
        self.setup_ui()
        self.setup_timer()
    
    def setup_ui(self):
        """设置UI界面"""
        self.setWindowTitle("ProjecTo 机械臂控制演示")
        self.setGeometry(100, 100, 1000, 700)
        
        # 主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 标题
        title = QLabel("ProjecTo - SO101机械臂控制演示")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # 连接控制区域
        connection_layout = QHBoxLayout()
        
        self.connect_btn = QPushButton("连接机械臂")
        self.connect_btn.clicked.connect(self.connect_robot)
        connection_layout.addWidget(self.connect_btn)
        
        self.disconnect_btn = QPushButton("断开连接")
        self.disconnect_btn.clicked.connect(self.disconnect_robot)
        self.disconnect_btn.setEnabled(False)
        connection_layout.addWidget(self.disconnect_btn)
        
        self.mock_btn = QPushButton("模拟模式")
        self.mock_btn.clicked.connect(self.connect_mock_robot)
        connection_layout.addWidget(self.mock_btn)
        
        self.status_label = QLabel("状态: 未连接")
        connection_layout.addWidget(self.status_label)
        
        layout.addLayout(connection_layout)
        
        # 控制面板
        control_layout = QHBoxLayout()
        
        # 左侧：关节控制滑块
        joint_control = QVBoxLayout()
        joint_control.addWidget(QLabel("关节位置控制:"))
        
        self.joint_sliders = {}
        self.joint_labels = {}
        
        joints = ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll"]
        
        for joint in joints:
            joint_layout = QHBoxLayout()
            
            label = QLabel(f"{joint}:")
            label.setMinimumWidth(100)
            joint_layout.addWidget(label)
            
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setMinimum(-2048)
            slider.setMaximum(2048)
            slider.setValue(0)
            slider.valueChanged.connect(lambda value, j=joint: self.on_slider_changed(j, value))
            joint_layout.addWidget(slider)
            
            value_label = QLabel("0")
            value_label.setMinimumWidth(50)
            joint_layout.addWidget(value_label)
            
            self.joint_sliders[joint] = slider
            self.joint_labels[joint] = value_label
            
            joint_control.addLayout(joint_layout)
        
        control_layout.addLayout(joint_control)
        
        # 右侧：预设位置和操作
        preset_control = QVBoxLayout()
        preset_control.addWidget(QLabel("预设位置:"))
        
        self.rest_btn = QPushButton("休息位置")
        self.rest_btn.clicked.connect(lambda: self.move_to_preset("rest"))
        preset_control.addWidget(self.rest_btn)
        
        self.v_btn = QPushButton("V字位置")
        self.v_btn.clicked.connect(lambda: self.move_to_preset("V"))
        preset_control.addWidget(self.v_btn)
        
        self.tracking_btn = QPushButton("追踪位置")
        self.tracking_btn.clicked.connect(lambda: self.move_to_preset("tracking"))
        preset_control.addWidget(self.tracking_btn)
        
        preset_control.addWidget(QLabel("位置管理:"))
        
        self.save_current_btn = QPushButton("保存当前位置")
        self.save_current_btn.clicked.connect(self.save_current_position)
        preset_control.addWidget(self.save_current_btn)
        
        self.read_current_btn = QPushButton("读取当前位置")
        self.read_current_btn.clicked.connect(self.read_current_position)
        preset_control.addWidget(self.read_current_btn)
        
        control_layout.addLayout(preset_control)
        
        layout.addLayout(control_layout)
        
        # 日志显示
        log_label = QLabel("操作日志:")
        layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        # 初始状态
        self.set_controls_enabled(False)
    
    def setup_timer(self):
        """设置定时器"""
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1000)  # 每秒更新一次
    
    def connect_robot(self):
        """连接真实机械臂"""
        if not LEROBOT_INTEGRATION_AVAILABLE:
            self.log("错误: LeRobot集成不可用")
            return
        
        try:
            self.log("正在连接SO101机械臂...")
            
            # 创建配置（仅Follower，不包含夹爪）
            self.robot_config = create_projecto_follower_only_config(
                follower_port="COM4",
                camera_index=0,
                include_gripper=False,
                mock=False
            )
            
            # 创建机械臂控制器
            self.robot = ManipulatorRobot(self.robot_config)
            
            # 连接
            if self.robot.connect():
                self.is_connected = True
                self.connect_btn.setEnabled(False)
                self.disconnect_btn.setEnabled(True)
                self.set_controls_enabled(True)
                self.log("✅ 机械臂连接成功")
                self.update_sliders_from_robot()
            else:
                self.log("❌ 机械臂连接失败")
                
        except Exception as e:
            self.log(f"❌ 连接错误: {e}")
    
    def connect_mock_robot(self):
        """连接模拟机械臂"""
        try:
            self.log("正在连接模拟机械臂...")
            
            # 创建模拟配置
            self.robot_config = create_projecto_follower_only_config(
                follower_port="COM4",
                camera_index=0,
                include_gripper=False,
                mock=True
            )
            
            # 创建机械臂控制器
            self.robot = ManipulatorRobot(self.robot_config)
            
            # 连接
            if self.robot.connect():
                self.is_connected = True
                self.connect_btn.setEnabled(False)
                self.disconnect_btn.setEnabled(True)
                self.set_controls_enabled(True)
                self.log("🎭 模拟机械臂连接成功")
                self.update_sliders_from_robot()
            else:
                self.log("❌ 模拟机械臂连接失败")
                
        except Exception as e:
            self.log(f"❌ 模拟连接错误: {e}")
    
    def disconnect_robot(self):
        """断开机械臂连接"""
        if self.robot:
            self.robot.disconnect()
            self.robot = None
            self.robot_config = None
        
        self.is_connected = False
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)
        self.set_controls_enabled(False)
        self.log("✅ 机械臂已断开连接")
    
    def set_controls_enabled(self, enabled: bool):
        """设置控件启用状态"""
        for slider in self.joint_sliders.values():
            slider.setEnabled(enabled)
        
        self.rest_btn.setEnabled(enabled)
        self.v_btn.setEnabled(enabled)
        self.tracking_btn.setEnabled(enabled)
        self.save_current_btn.setEnabled(enabled)
        self.read_current_btn.setEnabled(enabled)
    
    def on_slider_changed(self, joint: str, value: int):
        """滑块值改变回调"""
        self.joint_labels[joint].setText(str(value))
        
        if self.robot and self.is_connected:
            # 实时发送位置命令
            positions = {joint: float(value)}
            self.robot.move_to_position(positions)
    
    def move_to_preset(self, preset_name: str):
        """移动到预设位置"""
        if not self.robot or not self.is_connected:
            self.log("错误: 机械臂未连接")
            return
        
        if preset_name in self.saved_positions:
            positions = self.saved_positions[preset_name]
            self.log(f"移动到预设位置: {preset_name}")
            
            # 更新滑块
            for joint, value in positions.items():
                if joint in self.joint_sliders:
                    self.joint_sliders[joint].setValue(int(value))
            
            # 发送到机械臂
            self.robot.move_to_position(positions)
        else:
            self.log(f"警告: 预设位置 {preset_name} 不存在")
    
    def save_current_position(self):
        """保存当前位置"""
        if not self.robot or not self.is_connected:
            self.log("错误: 机械臂未连接")
            return
        
        try:
            # 从滑块获取当前位置
            current_positions = {}
            for joint, slider in self.joint_sliders.items():
                current_positions[joint] = float(slider.value())
            
            # 保存为新的预设
            position_name = f"saved_{int(time.time())}"
            self.saved_positions[position_name] = current_positions
            self.save_positions_to_file()
            
            self.log(f"✅ 位置已保存为: {position_name}")
            
        except Exception as e:
            self.log(f"❌ 保存位置失败: {e}")
    
    def read_current_position(self):
        """读取机械臂当前位置"""
        if not self.robot or not self.is_connected:
            self.log("错误: 机械臂未连接")
            return
        
        try:
            positions = self.robot.get_current_positions()
            self.log("当前机械臂位置:")
            for joint, pos in positions.items():
                self.log(f"  {joint}: {pos}")
            
            # 更新滑块
            self.update_sliders_from_positions(positions)
            
        except Exception as e:
            self.log(f"❌ 读取位置失败: {e}")
    
    def update_sliders_from_robot(self):
        """从机械臂更新滑块位置"""
        if self.robot:
            try:
                positions = self.robot.get_current_positions()
                self.update_sliders_from_positions(positions)
            except Exception as e:
                self.log(f"更新滑块失败: {e}")
    
    def update_sliders_from_positions(self, positions: dict):
        """从位置字典更新滑块"""
        for joint, pos in positions.items():
            if joint in self.joint_sliders:
                self.joint_sliders[joint].setValue(int(pos))
                self.joint_labels[joint].setText(str(int(pos)))
    
    def load_saved_positions(self):
        """加载保存的位置"""
        positions_file = Path(__file__).parent.parent / "config" / "saved_positions.json"
        
        # 默认位置
        self.saved_positions = {
            "rest": {
                "shoulder_pan": 0,
                "shoulder_lift": -1024,
                "elbow_flex": 1024,
                "wrist_flex": 0,
                "wrist_roll": 0,
            },
            "V": {
                "shoulder_pan": 0,
                "shoulder_lift": -1024,
                "elbow_flex": 2048,
                "wrist_flex": -1024,
                "wrist_roll": 0,
            },
            "tracking": {
                "shoulder_pan": 0,
                "shoulder_lift": -512,
                "elbow_flex": 1536,
                "wrist_flex": -512,
                "wrist_roll": 0,
            }
        }
        
        try:
            if positions_file.exists():
                with open(positions_file, 'r', encoding='utf-8') as f:
                    saved_data = json.load(f)
                    self.saved_positions.update(saved_data)
                self.log(f"✅ 已加载位置配置: {positions_file}")
        except Exception as e:
            self.log(f"⚠️ 加载位置配置失败: {e}")
    
    def save_positions_to_file(self):
        """保存位置到文件"""
        positions_file = Path(__file__).parent.parent / "config" / "saved_positions.json"
        
        try:
            positions_file.parent.mkdir(parents=True, exist_ok=True)
            with open(positions_file, 'w', encoding='utf-8') as f:
                json.dump(self.saved_positions, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.log(f"⚠️ 保存位置配置失败: {e}")
    
    def update_status(self):
        """更新状态显示"""
        if self.robot and self.is_connected:
            mode = "模拟模式" if self.robot.is_mock() else "真实模式"
            self.status_label.setText(f"状态: 已连接 ({mode})")
        else:
            self.status_label.setText("状态: 未连接")
    
    def log(self, message: str):
        """添加日志"""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        self.log_text.append(log_message)
        print(log_message)
    
    def closeEvent(self, event):
        """关闭事件"""
        if self.robot:
            self.disconnect_robot()
        event.accept()

def main():
    """主函数"""
    print("=" * 50)
    print("ProjecTo 机械臂控制演示")
    print("=" * 50)
    
    if not LEROBOT_INTEGRATION_AVAILABLE:
        print("⚠️ LeRobot集成不可用，某些功能将被禁用")
    
    app = QApplication(sys.argv)
    app.setApplicationName("ProjecTo Robot Control Demo")
    
    window = RobotControlDemo()
    window.show()
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
