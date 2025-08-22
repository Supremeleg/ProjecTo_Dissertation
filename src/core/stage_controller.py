# -*- coding: utf-8 -*-
"""
阶段控制器
管理系统的多阶段交互流程
"""

from typing import Optional, Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

from ..config.settings import AppSettings

class StageController(QObject):
    """阶段控制器
    
    管理REST -> PRIMARY -> COMPLEX的多阶段交互流程
    """
    
    # 信号定义
    stage_changed = pyqtSignal(str, str)  # (old_stage, new_stage)
    stage_entered = pyqtSignal(str)       # 进入阶段
    stage_exited = pyqtSignal(str)        # 退出阶段
    
    def __init__(self, system):
        super().__init__()
        
        self.system = system
        self.current_stage = AppSettings.DEFAULT_STAGE
        self.previous_stage = None
        
        # 阶段状态
        self.stage_data = {}
        self.stage_timers = {}
        
        # 超时控制
        self.idle_timer = QTimer()
        self.idle_timer.timeout.connect(self._on_idle_timeout)
        self.idle_timeout_duration = 30000  # 30秒无操作回到REST
        
        print("阶段控制器初始化完成")
    
    def start(self) -> bool:
        """启动阶段控制器"""
        print("正在启动阶段控制器...")
        
        try:
            # 进入默认阶段
            self._enter_stage(self.current_stage)
            
            # 启动空闲定时器
            self._reset_idle_timer()
            
            print(f"✅ 阶段控制器启动成功，当前阶段: {self.current_stage}")
            return True
            
        except Exception as e:
            print(f"❌ 阶段控制器启动失败: {e}")
            return False
    
    def stop(self):
        """停止阶段控制器"""
        print("正在停止阶段控制器...")
        
        try:
            # 停止所有定时器
            self.idle_timer.stop()
            for timer in self.stage_timers.values():
                timer.stop()
            
            # 退出当前阶段
            if self.current_stage:
                self._exit_stage(self.current_stage)
            
            print("✅ 阶段控制器已停止")
            
        except Exception as e:
            print(f"⚠️ 阶段控制器停止时出现错误: {e}")
    
    def change_stage(self, new_stage: str, **kwargs) -> bool:
        """切换阶段"""
        if new_stage == self.current_stage:
            print(f"已在阶段 {new_stage}，无需切换")
            return True
        
        if not self._is_valid_stage(new_stage):
            print(f"无效的阶段名称: {new_stage}")
            return False
        
        print(f"阶段切换: {self.current_stage} -> {new_stage}")
        
        try:
            # 保存当前阶段数据
            if kwargs:
                self.stage_data[new_stage] = kwargs
            
            # 退出当前阶段
            old_stage = self.current_stage
            self._exit_stage(old_stage)
            
            # 进入新阶段
            self.previous_stage = old_stage
            self.current_stage = new_stage
            self._enter_stage(new_stage)
            
            # 发送信号
            self.stage_changed.emit(old_stage, new_stage)
            
            # 重置空闲定时器
            self._reset_idle_timer()
            
            print(f"✅ 阶段切换完成: {new_stage}")
            return True
            
        except Exception as e:
            print(f"❌ 阶段切换失败: {e}")
            return False
    
    def go_back(self) -> bool:
        """返回上一阶段"""
        if self.previous_stage:
            return self.change_stage(self.previous_stage)
        else:
            # 默认返回REST阶段
            return self.change_stage(AppSettings.Stage.REST)
    
    def go_to_rest(self) -> bool:
        """返回REST阶段"""
        return self.change_stage(AppSettings.Stage.REST)
    
    def _enter_stage(self, stage: str):
        """进入阶段"""
        print(f"进入阶段: {stage}")
        
        # 根据阶段执行相应的初始化
        if stage == AppSettings.Stage.REST:
            self._enter_rest_stage()
        elif stage == AppSettings.Stage.PRIMARY_INTERACTION:
            self._enter_primary_stage()
        elif stage == AppSettings.Stage.MENU_DETAIL:
            self._enter_menu_detail_stage()
        elif stage == AppSettings.Stage.OBJECT_RECOGNITION:
            self._enter_object_recognition_stage()
        elif stage == AppSettings.Stage.SMART_CONTROL:
            self._enter_smart_control_stage()
        elif stage == AppSettings.Stage.TRACKING_MODE:
            self._enter_tracking_mode_stage()
        elif stage == AppSettings.Stage.GAME_MODE:
            self._enter_game_mode_stage()
        elif stage == AppSettings.Stage.KEYBOARD_INPUT:
            self._enter_keyboard_input_stage()
        
        self.stage_entered.emit(stage)
    
    def _exit_stage(self, stage: str):
        """退出阶段"""
        print(f"退出阶段: {stage}")
        
        # 根据阶段执行相应的清理
        if stage == AppSettings.Stage.REST:
            self._exit_rest_stage()
        elif stage == AppSettings.Stage.PRIMARY_INTERACTION:
            self._exit_primary_stage()
        elif stage == AppSettings.Stage.MENU_DETAIL:
            self._exit_menu_detail_stage()
        elif stage == AppSettings.Stage.OBJECT_RECOGNITION:
            self._exit_object_recognition_stage()
        elif stage == AppSettings.Stage.SMART_CONTROL:
            self._exit_smart_control_stage()
        elif stage == AppSettings.Stage.TRACKING_MODE:
            self._exit_tracking_mode_stage()
        elif stage == AppSettings.Stage.GAME_MODE:
            self._exit_game_mode_stage()
        elif stage == AppSettings.Stage.KEYBOARD_INPUT:
            self._exit_keyboard_input_stage()
        
        self.stage_exited.emit(stage)
    
    # ==================== 各阶段的进入/退出方法 ====================
    
    def _enter_rest_stage(self):
        """进入REST阶段"""
        print("💤 进入待机状态")
        # 这里可以添加REST阶段的初始化逻辑
        # 例如：显示吸引注意的动画、关闭机械臂扭矩等
        
    def _exit_rest_stage(self):
        """退出REST阶段"""
        print("⚡ 退出待机状态")
        
    def _enter_primary_stage(self):
        """进入PRIMARY阶段"""
        print("🎯 进入基础交互阶段")
        # 启用基础手势识别、显示主菜单等
        
    def _exit_primary_stage(self):
        """退出PRIMARY阶段"""
        print("📤 退出基础交互阶段")
        
    def _enter_menu_detail_stage(self):
        """进入菜单详情阶段"""
        print("📋 进入菜单详情阶段")
        
    def _exit_menu_detail_stage(self):
        """退出菜单详情阶段"""
        print("📤 退出菜单详情阶段")
        
    def _enter_object_recognition_stage(self):
        """进入物体识别阶段"""
        print("👁️ 进入物体识别阶段")
        # 启用YOLO物体检测
        
    def _exit_object_recognition_stage(self):
        """退出物体识别阶段"""
        print("📤 退出物体识别阶段")
        
    def _enter_smart_control_stage(self):
        """进入智能控制阶段"""
        print("🏠 进入智能控制阶段")
        
    def _exit_smart_control_stage(self):
        """退出智能控制阶段"""
        print("📤 退出智能控制阶段")
        
    def _enter_tracking_mode_stage(self):
        """进入追踪模式阶段"""
        print("🎯 进入追踪模式阶段")
        # 启用机械臂追踪
        
    def _exit_tracking_mode_stage(self):
        """退出追踪模式阶段"""
        print("📤 退出追踪模式阶段")
        
    def _enter_game_mode_stage(self):
        """进入游戏模式阶段"""
        print("🎮 进入游戏模式阶段")
        
    def _exit_game_mode_stage(self):
        """退出游戏模式阶段"""
        print("📤 退出游戏模式阶段")
        
    def _enter_keyboard_input_stage(self):
        """进入键盘输入阶段"""
        print("⌨️ 进入键盘输入阶段")
        
    def _exit_keyboard_input_stage(self):
        """退出键盘输入阶段"""
        print("📤 退出键盘输入阶段")
    
    # ==================== 工具方法 ====================
    
    def _is_valid_stage(self, stage: str) -> bool:
        """检查阶段是否有效"""
        valid_stages = [
            AppSettings.Stage.REST,
            AppSettings.Stage.PRIMARY_INTERACTION,
            AppSettings.Stage.MENU_DETAIL,
            AppSettings.Stage.OBJECT_RECOGNITION,
            AppSettings.Stage.SMART_CONTROL,
            AppSettings.Stage.TRACKING_MODE,
            AppSettings.Stage.GAME_MODE,
            AppSettings.Stage.KEYBOARD_INPUT,
        ]
        return stage in valid_stages
    
    def _reset_idle_timer(self):
        """重置空闲定时器"""
        if self.current_stage != AppSettings.Stage.REST:
            self.idle_timer.start(self.idle_timeout_duration)
        else:
            self.idle_timer.stop()
    
    def _on_idle_timeout(self):
        """空闲超时处理"""
        print("⏰ 空闲超时，返回待机状态")
        self.go_to_rest()
    
    def on_user_activity(self):
        """用户活动检测"""
        # 重置空闲定时器
        self._reset_idle_timer()
    
    def get_stage_data(self, stage: str = None) -> Dict[str, Any]:
        """获取阶段数据"""
        target_stage = stage or self.current_stage
        return self.stage_data.get(target_stage, {})
    
    def set_stage_data(self, key: str, value: Any, stage: str = None):
        """设置阶段数据"""
        target_stage = stage or self.current_stage
        if target_stage not in self.stage_data:
            self.stage_data[target_stage] = {}
        self.stage_data[target_stage][key] = value
    
    def clear_stage_data(self, stage: str = None):
        """清除阶段数据"""
        target_stage = stage or self.current_stage
        if target_stage in self.stage_data:
            self.stage_data[target_stage].clear()
