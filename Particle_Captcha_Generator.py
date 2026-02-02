import numpy as np
import cv2
import tempfile
import base64
from PIL import Image, ImageDraw, ImageFont
import os
import random
import math


def generate_particle_video(text):
    width, height = 320, 120
    fps = 30
    duration = 3.0  # 稍微延长一点，给凝聚和消散留时间
    total_frames = int(fps * duration)

    # 1. 准备字体
    try:
        font = ImageFont.truetype("arialbd.ttf", 80)
    except:
        font = ImageFont.load_default()

    # 计算文字包围盒
    dummy_img = Image.new('L', (10, 10), 0)
    draw_d = ImageDraw.Draw(dummy_img)
    bbox = draw_d.textbbox((0, 0), text, font=font)
    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]

    # 2. 巨型掩码 (用于漂移)
    padding_x = 80
    padding_y = 40
    mask_w = width + padding_x * 2
    mask_h = height + padding_y * 2

    mask_img = Image.new('L', (mask_w, mask_h), 0)
    draw = ImageDraw.Draw(mask_img)
    draw.text(((mask_w - text_w) / 2, (mask_h - text_h) / 2 - 15), text, font=font, fill=255)
    full_mask_np = np.array(mask_img) > 128

    # 3. 初始化粒子
    particle_count = 3000
    # x, y, vx, vy
    p_pos = np.random.rand(particle_count, 2) * [width, height]

    # 4. 视频写入
    with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as f:
        temp_video_path = f.name

    fourcc = cv2.VideoWriter_fourcc(*'vp80')
    out = cv2.VideoWriter(temp_video_path, fourcc, fps, (width, height), isColor=False)

    if not out.isOpened():
        return None

    # 运动参数
    phase_x = random.uniform(0, math.pi * 2)
    freq_x = random.uniform(3.0, 5.0)

    # 5. 渲染循环
    for i in range(total_frames):
        frame = np.zeros((height, width), dtype=np.uint8)

        # --- 时间轴控制 (Time Curve) ---
        # progress: 0.0 -> 1.0
        progress = i / total_frames

        # 凝聚因子 (Cohesion Factor)
        # 0.0 = 完全混沌 (首尾)
        # 1.0 = 文字成型 (中间)
        # 使用正弦波：在 0.0 和 1.0 时为 0，在 0.5 时为 1
        # 我们用一个梯形曲线让它在中间停留久一点
        if progress < 0.2:  # 前 20% 渐入
            cohesion = progress / 0.2
        elif progress > 0.8:  # 后 20% 渐出
            cohesion = (1.0 - progress) / 0.2
        else:  # 中间 60% 保持
            cohesion = 1.0

        # 这一步是为了让消失更彻底：如果 cohesion 太小，强制为 0
        if cohesion < 0.05: cohesion = 0

        # --- 漂移逻辑 ---
        # 文字依然在正弦漂移
        offset_x = int(padding_x + math.sin(progress * freq_x * math.pi + phase_x) * 50)
        offset_y = padding_y

        # --- 物理引擎 ---
        px = p_pos[:, 0].astype(int)
        py = p_pos[:, 1].astype(int)
        np.clip(px, 0, width - 1, out=px)
        np.clip(py, 0, height - 1, out=py)

        # 采样掩码
        sample_x = px + offset_x
        sample_y = py + offset_y
        np.clip(sample_x, 0, mask_w - 1, out=sample_x)
        np.clip(sample_y, 0, mask_h - 1, out=sample_y)

        # 判断是否在文字结构上
        in_text_structure = full_mask_np[sample_y, sample_x]

        # --- 速度场 (Velocity Field) ---

        # 基础风速 (所有粒子都在动)
        base_wind = 16.0

        # 初始化速度
        vx = np.zeros(particle_count)
        vy = np.zeros(particle_count)

        # 1. 默认行为：狂风 (Chaos)
        # 加上随机噪声
        vx[:] = base_wind + np.random.uniform(-4, 4, particle_count)
        vy[:] = np.random.uniform(-4, 4, particle_count)

        # 2. 文字行为：阻力 (Order)
        # 只有当 cohesion > 0 时，文字区域的粒子才会减速显形
        if cohesion > 0.3:
            # 找到在文字结构内的粒子
            text_indices = np.where(in_text_structure)[0]

            # 计算目标速度 (比狂风慢)
            target_vx = base_wind * 0.7

            # 线性插值 (Lerp): 根据 cohesion 因子混合 "狂风速度" 和 "文字速度"
            # 当 cohesion=1 时，完全显示文字动态；当 cohesion=0 时，完全是狂风
            current_vx = vx[text_indices]
            final_vx = current_vx * (1 - cohesion) + target_vx * cohesion

            # 赋予新速度 (+ 随机扰动防止死板)
            vx[text_indices] = final_vx + np.random.uniform(-1, 1, len(text_indices))
            vy[text_indices] *= (1 - cohesion)  # 垂直方向也减速

            # 视觉增强：如果在显示文字阶段，增加文字区域粒子的亮度/密度感知
            # 我们通过让粒子稍微聚拢一点来实现 (Position Correction)
            # 这里简单起见，利用速度差已经能产生视觉积聚效果

        # 更新位置
        p_pos[:, 0] += vx
        p_pos[:, 1] += vy

        # 循环边界
        respawn_mask = (p_pos[:, 0] >= width)
        p_pos[respawn_mask, 0] = 0
        p_pos[respawn_mask, 1] = np.random.uniform(0, height, np.sum(respawn_mask))

        # --- 绘制 ---
        draw_x = p_pos[:, 0].astype(int)
        draw_y = p_pos[:, 1].astype(int)
        np.clip(draw_x, 0, width - 2, out=draw_x)
        np.clip(draw_y, 0, height - 2, out=draw_y)

        frame[draw_y, draw_x] = 255
        frame[draw_y + 1, draw_x] = 255
        frame[draw_y, draw_x + 1] = 255

        # 写入
        out.write(frame)

    out.release()

    with open(temp_video_path, 'rb') as f:
        video_data = f.read()
    try:
        os.remove(temp_video_path)
    except:
        pass

    return base64.b64encode(video_data).decode()
