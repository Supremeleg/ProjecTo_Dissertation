# ProjecTo 安装指南

## 系统要求

### 基本要求
- Python 3.8 或更高版本
- Windows 10/11, macOS 10.15+, 或 Ubuntu 18.04+
- 至少 4GB RAM
- 支持 OpenGL 3.3 的显卡

### 硬件要求（可选）
- USB 摄像头（用于手势识别）
- 兼容 LeRobot 的机械臂（用于物理交互）

## 安装步骤

### 1. 克隆项目

```bash
git clone https://github.com/your-username/ProjecTo.git
cd ProjecTo
```

### 2. 创建虚拟环境

```bash
# 使用 venv
python -m venv projecto_env

# 激活虚拟环境
# Windows:
projecto_env\Scripts\activate
# macOS/Linux:
source projecto_env/bin/activate
```

### 3. 安装依赖

#### 基础安装（仅视觉交互）
```bash
pip install -r requirements.txt
```

#### 完整安装（包含机械臂支持）
```bash
# 首先安装基础依赖
pip install -r requirements.txt

# 安装 LeRobot 框架
pip install lerobot

# 安装额外的机械臂依赖
pip install dynamixel-sdk>=3.7.51
```

### 4. 验证安装

```bash
# 运行系统信息检查
python -c "import projecto; projecto.print_system_info()"

# 运行演示程序
python examples/demo.py
```

## 配置

### 摄像头配置

1. 运行摄像头测试：
```bash
python scripts/test_camera.py
```

2. 如果需要调整摄像头设置，编辑 `config/camera_config.json`：
```json
{
  "camera_index": 0,
  "width": 320,
  "height": 240,
  "fps": 30
}
```

### 机械臂配置（可选）

1. 确保机械臂硬件正确连接
2. 运行机械臂测试：
```bash
python scripts/test_robot.py
```

3. 调整机械臂配置 `config/robot_config.json`：
```json
{
  "follower_port": "COM4",
  "servo_port": "COM3",
  "servo_baudrate": 9600
}
```

## 运行模式

### 1. 完整模式（需要摄像头和机械臂）
```bash
python src/main.py --enable-robot
```

### 2. 仅视觉模式（只需要摄像头）
```bash
python src/main_vision_only.py
```

### 3. 演示模式（无需硬件）
```bash
python examples/demo.py
```

### 4. 调试模式
```bash
python src/main.py --debug --windowed
```

## 故障排除

### 常见问题

#### 1. 摄像头无法初始化
```bash
# 检查摄像头是否被其他程序占用
# 尝试不同的摄像头索引
python scripts/test_camera.py --camera-index 1
```

#### 2. 机械臂连接失败
```bash
# 检查串口权限（Linux/macOS）
sudo usermod -a -G dialout $USER
# 重新登录后生效

# 检查端口是否正确
python scripts/list_serial_ports.py
```

#### 3. 依赖安装失败
```bash
# 更新 pip
pip install --upgrade pip

# 使用镜像源（中国大陆用户）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

#### 4. PyQt6 安装问题
```bash
# Ubuntu/Debian
sudo apt-get install python3-pyqt6

# macOS
brew install pyqt6

# Windows
# 使用官方安装包或 conda
conda install pyqt6
```

### 性能优化

#### 1. 降低摄像头分辨率
在 `config/camera_config.json` 中设置更小的分辨率：
```json
{
  "width": 160,
  "height": 120
}
```

#### 2. 调整处理频率
在 `config/settings.py` 中调整：
```python
VISION_SKIP_FRAMES = 3  # 每4帧处理1帧
GESTURE_PROCESS_INTERVAL = 100  # 100ms间隔
```

## 开发环境设置

### 安装开发工具
```bash
pip install -e .[dev]
```

### 代码格式化
```bash
black src/ examples/ tests/
```

### 类型检查
```bash
mypy src/
```

### 运行测试
```bash
pytest tests/
```

## Docker 部署（实验性）

```bash
# 构建镜像
docker build -t projecto .

# 运行容器（仅视觉模式）
docker run -it --rm \
  --device=/dev/video0 \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  projecto python src/main_vision_only.py
```

## 卸载

```bash
# 停用虚拟环境
deactivate

# 删除虚拟环境
rm -rf projecto_env

# 删除项目文件
cd ..
rm -rf ProjecTo
```
