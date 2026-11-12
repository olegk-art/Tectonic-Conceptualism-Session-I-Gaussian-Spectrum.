import numpy as np
import svgwrite
import math
import hashlib
import datetime

def get_sha256(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def generate_base_with_burn(filename, outer_w=465, outer_h=205, phantom_w=310, phantom_h=125, margin=15):
    dwg = svgwrite.Drawing(
        filename, 
        size=(f"{outer_w}mm", f"{outer_h}mm"), 
        viewBox=f"0 0 {outer_w} {outer_h}", 
        profile='tiny'
    )
    
    # --- КООРДИНАТЫ ---
    px_min = (outer_w - phantom_w) / 2
    py_min = (outer_h - phantom_h) / 2
    px_max = px_min + phantom_w
    py_max = py_min + phantom_h
    cx = outer_w / 2
    cy = outer_h / 2

    # --- СЛОЙ 1: КРАСНЫЙ (ВНЕШНИЙ ПЕРИМЕТР - CUT) ---
    dwg.add(dwg.rect(insert=(0, 0), size=(outer_w, outer_h), fill='none', stroke='red', stroke_width=0.2))

    # --- СЛОЙ 2: СИНИЙ (МИКРО-ПЕРФОРАЦИЯ - CUT) ---
    # Логика Базы: Крупные элементы в центре, мелкие к краям фантома
    np.random.seed(42) 
    step = 5.0  # Шаг реже, чем у Ядра, так как элементы крупнее
    
    for x in np.arange(px_min + 2, px_max - 2, step):
        for y in np.arange(py_min + 2, py_max - 2, step):
            px = x + np.random.uniform(-1.0, 1.0)
            py = y + np.random.uniform(-1.0, 1.0)
            
            dist_center = math.hypot(px - cx, py - cy)
            max_dist_center = math.hypot(phantom_w/2, phantom_h/2)
            norm_dist = dist_center / max_dist_center
            
            # ИНВЕРСИЯ БАЗЫ: Размер уменьшается от центра к краям (3.5 -> 1.5)
            size = 3.5 - (norm_dist * 2.0)
            size = max(1.2, min(size, 3.5))
            
            # Небольшая безопасная зона у краев, чтобы элементы не вылетали
            dist_to_edge = min(px - px_min, px_max - px, py - py_min, py_max - py)
            if dist_to_edge < 3.0:
                continue 

            dwg.add(dwg.rect(
                insert=(px - size/2, py - size/2), 
                size=(size, size), 
                fill='none', 
                stroke='blue', 
                stroke_width=0.3
            ))

    # --- СЛОЙ 3: ЧЕРНЫЙ (СКВОЗНЫЕ МАКРО-ВЕКТОРЫ: ЭКСПАНСИЯ - CUT) ---
    num_rays = 16 
    ray_angles = []
    for i in range(num_rays):
        angle = (2 * math.pi / num_rays) * i
        angle += np.random.uniform(-0.15, 0.15)
        ray_angles.append(angle)
        
        # Луч идет ОТ ЦЕНТРА к периферии
        start_r = 10.0 # Начинаем не с самого центра
        p1 = (cx + start_r * math.cos(angle), cy + start_r * math.sin(angle))
        
        if math.cos(angle) > 0:
            limit_x = (outer_w - margin - cx) / math.cos(angle)
        else:
            limit_x = (margin - cx) / math.cos(angle)
        if math.sin(angle) > 0:
            limit_y = (outer_h - margin - cy) / math.sin(angle)
        else:
            limit_y = (margin - cy) / math.sin(angle)
            
        end_r = min(abs(limit_x), abs(limit_y))
        p2 = (cx + end_r * math.cos(angle), cy + end_r * math.sin(angle))
        
        # Перемычки для сохранения структуры
        seg1_end = 0.35
        seg2_start = 0.65
        
        p_mid1 = (p1[0] + (p2[0] - p1[0]) * seg1_end, p1[1] + (p2[1] - p1[1]) * seg1_end)
        p_mid2 = (p1[0] + (p2[0] - p1[0]) * seg2_start, p1[1] + (p2[1] - p1[1]) * seg2_start)
        
        noise_x = np.random.uniform(-2.0, 2.0)
        noise_y = np.random.uniform(-2.0, 2.0)
        p_mid1_noisy = (p_mid1[0] + noise_x, p_mid1[1] + noise_y)
        p_mid2_noisy = (p_mid2[0] + noise_x, p_mid2[1] + noise_y)
        
        dwg.add(dwg.line(start=p1, end=p_mid1_noisy, stroke='black', stroke_width=0.4))
        dwg.add(dwg.line(start=p_mid2_noisy, end=p2, stroke='black', stroke_width=0.4))

    # --- СЛОЙ 4: ЗЕЛЕНЫЙ (ТЕРМИЧЕСКИЙ ОБЖИГ / GUE + DLA + JITTER - FILL) ---
    # Плотность снижена (шаг 1.25, порог 0.40)
    burn_step = 1.25 
    np.random.seed(2026) 

    for x in np.arange(0, outer_w, burn_step):
        for y in np.arange(0, outer_h, burn_step):
            # Джиттер сетки (смещение для органичности)
            px_burn = x + np.random.uniform(-0.8, 0.8)
            py_burn = y + np.random.uniform(-0.8, 0.8)
            
            # Не жжем за пределами безопасной зоны (margin)
            if not (margin < px_burn < outer_w - margin and margin < py_burn < outer_h - margin):
                continue
                
            theta = math.atan2(py_burn - cy, px_burn - cx)
            
            # 1. DLA: Расчет расстояния до ближайшего макро-разреза (луча)
            min_angle_diff = float('inf')
            for ray_angle in ray_angles:
                diff = abs(theta - ray_angle)
                if diff > math.pi:
                    diff = 2 * math.pi - diff
                min_angle_diff = min(min_angle_diff, diff)
            
            # 2. DLA: Расчет расстояния до границ внутренней зоны фантома (310x125)
            dist_to_box_edge = min(abs(px_burn - px_min), abs(px_burn - px_max), abs(py_burn - py_min), abs(py_burn - py_max))
            
            # 3. GUE: Гауссов шум для энтропии
            gue_noise = abs(np.random.normal(0, 0.5))
            
            # Формула интенсивности обжига
            intensity_ray = math.exp(-min_angle_diff * 4.0) 
            intensity_edge = math.exp(-dist_to_box_edge * 0.2) 
            
            # Порог вероятности 0.40
            prob = (intensity_ray * 0.6 + intensity_edge * 0.4) + gue_noise * 0.2
            
            if prob > 0.40:
                # Радиус точки уменьшен для легкости обжига
                dot_radius = 0.15 + (gue_noise * 0.15)
                
                dwg.add(dwg.circle(center=(px_burn, py_burn), r=dot_radius, fill='green', stroke='none'))

    dwg.save()
    print(f"Сохранено: {filename}")
    
    # --- ВЕРИФИКАЦИЯ (P7) ---
    file_hash = get_sha256(filename)
    print(f"SHA-256: {file_hash}")
    
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    ledger_filename = filename.replace('.svg', '_ledger.txt')
    with open(ledger_filename, 'w') as f:
        f.write(f"NODE: M_001_BASE (BURN + JITTER - OPTIMIZED)\n")
        f.write(f"FILE: {filename}\n")
        f.write(f"TIMESTAMP: {timestamp}\n")
        f.write(f"SHA-256: {file_hash}\n")
        f.write(f"STATUS: VERIFIED\n")
    print(f"Ledger сохранен: {ledger_filename}\n")

if __name__ == '__main__':
    generate_base_with_burn('base_hybrid_burn.svg')