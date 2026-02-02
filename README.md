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
