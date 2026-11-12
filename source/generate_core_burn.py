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

def generate_core_with_burn(filename, outer_w=325, outer_h=145, inner_w=310, inner_h=125, margin=7.5):
    dwg = svgwrite.Drawing(
        filename, 
        size=(f"{outer_w}mm", f"{outer_h}mm"), 
        viewBox=f"0 0 {outer_w} {outer_h}", 
        profile='tiny'
    )
    
    # --- КООРДИНАТЫ ---
    px_min = (outer_w - inner_w) / 2
    py_min = (outer_h - inner_h) / 2
    px_max = px_min + inner_w
    py_max = py_min + inner_h
    cx = outer_w / 2
    cy = outer_h / 2

    # --- СЛОЙ 1: КРАСНЫЙ (ВНЕШНИЙ ПЕРИМЕТР - CUT) ---
    dwg.add(dwg.rect(insert=(0, 0), size=(outer_w, outer_h), fill='none', stroke='red', stroke_width=0.2))

    # --- СЛОЙ 2: СИНИЙ (МИКРО-ПЕРФОРАЦИЯ - CUT) ---
    np.random.seed(108) 
    step = 3.6           
    edge_safe_zone = 5.0 
    
    for x in np.arange(px_min + edge_safe_zone, px_max - edge_safe_zone, step):
        for y in np.arange(py_min + edge_safe_zone, py_max - edge_safe_zone, step):
            px = x + np.random.uniform(-0.5, 0.5)
            py = y + np.random.uniform(-0.5, 0.5)
            
            dist_center = math.hypot(px - cx, py - cy)
            max_dist_center = math.hypot(inner_w/2, inner_h/2)
            norm_dist = dist_center / max_dist_center
            
            skip_prob = 0.15 + (norm_dist * 0.35) 
            if np.random.rand() < skip_prob:
                continue
                
            size = 1.2 + (norm_dist * 1.8) 
            size = max(1.2, min(size, 3.0))
            
            dist_to_edge = min(px - px_min, px_max - px, py - py_min, py_max - py)
            if dist_to_edge < edge_safe_zone:
                continue 

            dwg.add(dwg.rect(
                insert=(px - size/2, py - size/2), 
                size=(size, size), 
                fill='none', 
                stroke='blue', 
                stroke_width=0.3
            ))

    # --- СЛОЙ 3: ЧЕРНЫЙ (СКВОЗНЫЕ МАКРО-ВЕКТОРЫ - CUT) ---
    num_rays = 12 
    ray_angles = []
    for i in range(num_rays):
        angle = (2 * math.pi / num_rays) * i
        angle += np.random.uniform(-0.2, 0.2)
        ray_angles.append(angle)
        
        if math.cos(angle) > 0:
            limit_x = (outer_w - margin - cx) / math.cos(angle)
        else:
            limit_x = (margin - cx) / math.cos(angle)
        if math.sin(angle) > 0:
            limit_y = (outer_h - margin - cy) / math.sin(angle)
        else:
            limit_y = (margin - cy) / math.sin(angle)
            
        start_r = min(abs(limit_x), abs(limit_y))
        p1 = (cx + start_r * math.cos(angle), cy + start_r * math.sin(angle))
        
        end_r = 15.0 
        p2 = (cx + end_r * math.cos(angle), cy + end_r * math.sin(angle))
        
        seg1_end = 0.4
        seg2_start = 0.7
        
        p_mid1 = (p1[0] + (p2[0] - p1[0]) * seg1_end, p1[1] + (p2[1] - p1[1]) * seg1_end)
        p_mid2 = (p1[0] + (p2[0] - p1[0]) * seg2_start, p1[1] + (p2[1] - p1[1]) * seg2_start)
        
        noise_x = np.random.uniform(-1.5, 1.5)
        noise_y = np.random.uniform(-1.5, 1.5)
        p_mid1_noisy = (p_mid1[0] + noise_x, p_mid1[1] + noise_y)
        p_mid2_noisy = (p_mid2[0] + noise_x, p_mid2[1] + noise_y)
        
        dwg.add(dwg.line(start=p1, end=p_mid1_noisy, stroke='black', stroke_width=0.4))
        dwg.add(dwg.line(start=p_mid2_noisy, end=p2, stroke='black', stroke_width=0.4))

    # --- СЛОЙ 4: ЗЕЛЕНЫЙ (ТЕРМИЧЕСКИЙ ОБЖИГ / GUE + DLA + JITTER - FILL) ---
    # Плотность уменьшена на ~40%: шаг увеличен с 1.0 до 1.25, порог повышен до 0.40
    burn_step = 1.25 
    np.random.seed(2026) 

    for x in np.arange(0, outer_w, burn_step):
        for y in np.arange(0, outer_h, burn_step):
            # Джиттер сетки (смещение)
            px_burn = x + np.random.uniform(-0.8, 0.8)
            py_burn = y + np.random.uniform(-0.8, 0.8)
            
            if not (margin < px_burn < outer_w - margin and margin < py_burn < outer_h - margin):
                continue
                
            r = math.hypot(px_burn - cx, py_burn - cy)
            theta = math.atan2(py_burn - cy, px_burn - cx)
            
            # 1. DLA: Расстояние до макро-разрезов
            min_angle_diff = float('inf')
            for ray_angle in ray_angles:
                diff = abs(theta - ray_angle)
                if diff > math.pi:
                    diff = 2 * math.pi - diff
                min_angle_diff = min(min_angle_diff, diff)
            
            # 2. DLA: Расстояние до границ фантома
            dist_to_box_edge = min(abs(px_burn - px_min), abs(px_burn - px_max), abs(py_burn - py_min), abs(py_burn - py_max))
            
            # 3. GUE: Гауссов шум
            gue_noise = abs(np.random.normal(0, 0.5))
            
            intensity_ray = math.exp(-min_angle_diff * 4.0) 
            intensity_edge = math.exp(-dist_to_box_edge * 0.2) 
            
            # Порог вероятности повышен до 0.40 (было 0.35)
            prob = (intensity_ray * 0.6 + intensity_edge * 0.4) + gue_noise * 0.2
            
            if prob > 0.40:
                # Радиус точки немного уменьшен для легкости обжига
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
        f.write(f"NODE: M_002_CORE (BURN + JITTER - OPTIMIZED)\n")
        f.write(f"FILE: {filename}\n")
        f.write(f"TIMESTAMP: {timestamp}\n")
        f.write(f"SHA-256: {file_hash}\n")
        f.write(f"STATUS: VERIFIED (NFS)\n")
    print(f"Ledger сохранен: {ledger_filename}\n")

if __name__ == '__main__':
    generate_core_with_burn('core_hybrid_burn.svg')