#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ProjecTo 演示程序
展示系统的基本功能，不需要物理硬件
"""

import sys
import time
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QTextEdit
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont

from config.settings import AppSettings
from core.system import ProjecToSystem

class DemoWindow(QMainWindow):
    """演示窗口"""
    
    def __init__(self):
        super().__init__()
        self.system = None
        self.setup_ui()
        self.setup_system()
    
    def setup_ui(self):
        """设置UI界面"""
        self.setWindowTitle("ProjecTo 演示程序")
        self.setGeometry(100, 100, 800, 600)
        
        # 主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 标题
        title = QLabel("ProjecTo - 智能交互投影系统")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # 状态显示
        self.status_label = QLabel("系统状态: 未初始化")
        self.status_label.setFont(QFont("Arial", 12))
        layout.addWidget(self.status_label)
        
        # 阶段控制按钮
        stage_layout = QHBoxLayout()
        
        self.rest_btn = QPushButton("REST (待机)")
        self.rest_btn.clicked.connect(lambda: self.change_stage(AppSettings.Stage.REST))
        stage_layout.addWidget(self.rest_btn)
        
        self.primary_btn = QPushButton("PRIMARY (基础交互)")
        self.primary_btn.clicked.connect(lambda: self.change_stage(AppSettings.Stage.PRIMARY_INTERACTION))
        stage_layout.addWidget(self.primary_btn)
        
        self.menu_btn = QPushButton("MENU (菜单详情)")
        self.menu_btn.clicked.connect(lambda: self.change_stage(AppSettings.Stage.MENU_DETAIL))
        stage_layout.addWidget(self.menu_btn)
        
        self.object_btn = QPushButton("物体识别")
        self.object_btn.clicked.connect(lambda: self.change_stage(AppSettings.Stage.OBJECT_RECOGNITION))
        stage_layout.addWidget(self.object_btn)
        
        layout.addLayout(stage_layout)
        
        # 机械臂控制按钮（如果启用）
        robot_layout = QHBoxLayout()
        
        self.connect_robot_btn = QPushButton("连接机械臂")
        self.connect_robot_btn.clicked.connect(self.connect_robot)
        robot_layout.addWidget(self.connect_robot_btn)
        
        self.move_rest_btn = QPushButton("移动到休息位置")
        self.move_rest_btn.clicked.connect(lambda: self.move_robot("rest"))
        robot_layout.addWidget(self.move_rest_btn)
        
        self.move_v_btn = QPushButton("移动到V位置")
        self.move_v_btn.clicked.connect(lambda: self.move_robot("V"))
        robot_layout.addWidget(self.move_v_btn)
        
        self.nod_btn = QPushButton("点头动作")
        self.nod_btn.clicked.connect(self.robot_nod)
        robot_layout.addWidget(self.nod_btn)
        
        layout.addLayout(robot_layout)
        
        # 日志显示
        log_label = QLabel("系统日志:")
        layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(200)
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        # 控制按钮
        control_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("启动系统")
        self.start_btn.clicked.connect(self.start_system)
        control_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("停止系统")
        self.stop_btn.clicked.connect(self.stop_system)
        self.stop_btn.setEnabled(False)
        control_layout.addWidget(self.stop_btn)
        
        layout.addLayout(control_layout)
        
        # 更新定时器
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(1000)  # 每秒更新一次
    
    def setup_system(self):
        """设置系统"""
        # 强制禁用机械臂（演示模式）
        AppSettings.ENABLE_ROBOT = False
        AppSettings.DEBUG_MODE = True
        AppSettings.FULLSCREEN = False
        
        self.log("演示模式：机械臂功能已禁用")
    
    def start_system(self):
        """启动系统"""
        try:
            self.log("正在启动ProjecTo系统...")
            self.system = ProjecToSystem()
            
            # 连接信号
            self.system.system_ready.connect(self.on_system_ready)
            self.system.system_error.connect(self.on_system_error)
            self.system.stage_changed.connect(self.on_stage_changed)
            
            if self.system.start():
                self.start_btn.setEnabled(False)
                self.stop_btn.setEnabled(True)
                self.log("✅ 系统启动成功")
            else:
                self.log("❌ 系统启动失败")
        
        except Exception as e:
            self.log(f"❌ 启动系统时出错: {e}")
    
    def stop_system(self):
        """停止系统"""
        try:
            if self.system:
                self.system.stop()
                self.system = None
            
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.log("✅ 系统已停止")
        
        except Exception as e:
            self.log(f"⚠️ 停止系统时出错: {e}")
    
    def change_stage(self, stage: str):
        """切换阶段"""
        if self.system and self.system.is_running:
            if self.system.change_stage(stage):
                self.log(f"✅ 切换到阶段: {stage}")
            else:
                self.log(f"❌ 阶段切换失败: {stage}")
        else:
            self.log("⚠️ 系统未运行，无法切换阶段")
    
    def connect_robot(self):
        """连接机械臂"""
        self.log("演示模式：机械臂连接已禁用")
    
    def move_robot(self, position: str):
        """移动机械臂"""
        self.log(f"演示模式：模拟机械臂移动到 {position}")
    
    def robot_nod(self):
        """机械臂点头"""
        self.log("演示模式：模拟机械臂点头动作")
    
    def update_status(self):
        """更新状态显示"""
        if self.system and self.system.is_running:
            status = self.system.get_system_status()
            status_text = f"系统状态: 运行中 | 当前阶段: {status['current_stage']} | 机械臂: {'启用' if status['robot_enabled'] else '禁用'}"
            self.status_label.setText(status_text)
        else:
            self.status_label.setText("系统状态: 未运行")
    
    def on_system_ready(self):
        """系统就绪"""
        self.log("🎉 系统就绪")
    
    def on_system_error(self, error: str):
        """系统错误"""
        self.log(f"❌ 系统错误: {error}")
    
    def on_stage_changed(self, old_stage: str, new_stage: str):
        """阶段变化"""
        self.log(f"🔄 阶段变化: {old_stage} -> {new_stage}")
    
    def log(self, message: str):
        """添加日志"""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        self.log_text.append(log_message)
        print(log_message)
    
    def closeEvent(self, event):
        """关闭事件"""
        if self.system:
            self.stop_system()
        event.accept()

def main():
    """主函数"""
    print("=" * 50)
    print("ProjecTo 演示程序")
    print("=" * 50)
    
    app = QApplication(sys.argv)
    app.setApplicationName("ProjecTo Demo")
    
    window = DemoWindow()
    window.show()
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
