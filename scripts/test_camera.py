#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
摄像头测试脚本
用于测试和配置摄像头设备
"""

import cv2
import argparse
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(project_root))

def test_camera(camera_index=0, width=320, height=240, duration=10):
    """测试摄像头"""
    print(f"正在测试摄像头 {camera_index}...")
    print(f"分辨率: {width}x{height}")
    print(f"测试时长: {duration}秒")
    print("按 'q' 键退出")
    
    # 初始化摄像头
    cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        print(f"❌ 无法打开摄像头 {camera_index}")
        return False
    
    # 设置分辨率
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    
    # 获取实际分辨率
    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    actual_fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"✅ 摄像头初始化成功")
    print(f"实际分辨率: {actual_width}x{actual_height}")
    print(f"实际帧率: {actual_fps:.1f} FPS")
    
    frame_count = 0
    start_time = cv2.getTickCount()
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ 无法读取摄像头数据")
                break
            
            frame_count += 1
            
            # 计算FPS
            current_time = cv2.getTickCount()
            elapsed_time = (current_time - start_time) / cv2.getTickFrequency()
            
            if elapsed_time > 0:
                fps = frame_count / elapsed_time
                cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # 显示帧数和时间
            cv2.putText(frame, f"Frame: {frame_count}", (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Time: {elapsed_time:.1f}s", (10, 110), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # 显示图像
            cv2.imshow('Camera Test', frame)
            
            # 检查退出条件
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or elapsed_time >= duration:
                break
    
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断测试")
    
    finally:
        # 释放资源
        cap.release()
        cv2.destroyAllWindows()
        
        # 显示统计信息
        final_time = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()
        final_fps = frame_count / final_time if final_time > 0 else 0
        
        print(f"\n📊 测试统计:")
        print(f"总帧数: {frame_count}")
        print(f"总时长: {final_time:.2f}秒")
        print(f"平均FPS: {final_fps:.2f}")
        
        return True

def list_cameras():
    """列出可用的摄像头"""
    print("正在扫描可用摄像头...")
    available_cameras = []
    
    for i in range(10):  # 检查前10个设备
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            available_cameras.append({
                'index': i,
                'width': width,
                'height': height,
                'fps': fps
            })
            
            print(f"✅ 摄像头 {i}: {width}x{height} @ {fps:.1f}FPS")
            cap.release()
        else:
            print(f"❌ 摄像头 {i}: 不可用")
    
    if not available_cameras:
        print("⚠️ 未找到可用的摄像头")
    else:
        print(f"\n📋 找到 {len(available_cameras)} 个可用摄像头")
    
    return available_cameras

def main():
    parser = argparse.ArgumentParser(description="ProjecTo 摄像头测试工具")
    parser.add_argument("--camera-index", type=int, default=0, help="摄像头索引")
    parser.add_argument("--width", type=int, default=320, help="画面宽度")
    parser.add_argument("--height", type=int, default=240, help="画面高度")
    parser.add_argument("--duration", type=int, default=10, help="测试时长（秒）")
    parser.add_argument("--list", action="store_true", help="列出可用摄像头")
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("ProjecTo 摄像头测试工具")
    print("=" * 50)
    
    if args.list:
        list_cameras()
    else:
        test_camera(args.camera_index, args.width, args.height, args.duration)

if __name__ == "__main__":
    main()
