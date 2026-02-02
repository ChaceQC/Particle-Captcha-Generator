# 粒子流体动态验证码 (Particle Captcha Generator)

这是一个轻量级的 Python 脚本，用于生成**动态粒子流验证码**。
算法模拟了“风洞”物理环境：大量粒子在高速流动时，遇到不可见的文字阻挡层产生积聚从而显影，随后随风消散。

> **核心特性：**
> - 🌪 **物理模拟**：模拟粒子的速度场、凝聚效应和消散过程。
> - 🔒 **抗 OCR**：文字位置持续进行正弦漂移，且仅通过粒子密度差异成像，机器识别难度大。
> - ⚡ **前端友好**：直接返回内存中的 Base64 字符串（WebM 格式），无需落盘，可直接嵌入 HTML5 `<video>` 标签。
> - 🐍 **纯 Python**：基于 NumPy 和 OpenCV 构建，无复杂依赖。

## 安装依赖

```bash
pip install numpy opencv-python-headless pillow
```

## 快速开始

- 建议仅传入四位数字；

```python
import base64
from Particle_Captcha_Generator import generate_particle_video

# 1. 生成验证码 (返回 base64 字符串)
video_b64 = generate_particle_video("6669")

# 2. 前端嵌入示例
html_snippet = f'<video src="data:video/webm;base64,{video_b64}" autoplay loop>'
print(f"视频已生成，Base64长度: {len(video_b64)}")
```

## 示例展示

[tmpnjw0kld0.webm](https://github.com/user-attachments/assets/981da5b2-6049-4a8c-a833-1a1ccff42aea)

## ⚙️ 参数详情 (Configuration)

目前参数位于 `generate_particle_video` 函数内部，可根据需要直接修改变量值：

### 1. 基础视频参数
| 变量名 | 默认值 | 说明 |
| :--- | :--- | :--- |
| `width`, `height` | `320`, `120` | 视频画布的分辨率（像素）。 |
| `fps` | `30` | 帧率。降低此值可显著减小生成体积。 |
| `duration` | `3.0` | 视频总时长（秒）。包含渐入、保持和消散三个阶段。 |

### 2. 粒子物理参数
| 变量名 | 默认值 | 说明 | 影响 |
| :--- | :--- | :--- | :--- |
| `particle_count` | `3000` | 屏幕上的总粒子数量。 | **核心参数**。数量越多文字越清晰，但 CPU 计算开销越大。 |
| `base_wind` | `16.0` | 粒子的基础飞行速度。 | 值越大，粒子流速越快，视觉上的“狂风”感越强。 |
| `target_vx` | `11.2` | 粒子撞击文字后的目标速度。 | 通常设为 `base_wind * 0.7`。与风速差值越大，文字积聚越明显。 |

### 3. 动画与干扰参数
| 变量名 | 默认值 | 说明 |
| :--- | :--- | :--- |
| `freq_x` | `3.0~5.0` | 文字水平漂移的频率（随机值）。控制文字左右晃动的速度。 |
| `cohesion` | `0.0~1.0` | **凝聚因子**。控制文字从混沌到成型的时间曲线。目前逻辑为：前 20% 渐入，中间 60% 保持，后 20% 消散。 |

## 🛠 调整指南 (Tuning Guide)

### 场景 A：追求高性能 (Performance First)
如果生成速度太慢或服务器负载过高：
1. **降低 `particle_count`**：降至 `2000` 或 `1500`。
2. **缩小画布**：将 `width, height` 改为 `200, 80`。
3. **降低帧率**：将 `fps` 降为 `20` 或 `15`。

### 场景 B：追求文字清晰度 (Readability First)
如果用户反馈验证码难以辨认：
1. **增加 `particle_count`**：升至 `4000` 或 `5000`。
2. **增大速度差**：降低 `target_vx` 系数（例如 `base_wind * 0.5`）。
3. **减弱漂移**：将 `freq_x` 的随机范围调低。

### 场景 C：提高安全性 (Security First)
如果要防止 AI 破解：
1. **增加漂移幅度**：增大代码中 `math.sin(...) * 50` 里的 `50`。
2. **缩短保持时间**：修改 `cohesion` 的逻辑，减少中间“完全清晰”的时间窗口。
