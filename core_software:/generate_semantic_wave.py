# -*- coding: utf-8 -*-
import hashlib
import random
import os
import math

machine_responses = ["ааааааёчям", "аааааабсус"]

def generate_wave_interference_svg(text_seed, filename, mediator_w, mediator_h, visible_w, visible_h, label_prefix, target_id):
    """
    Прецизионный генератор интерференционных волн Френеля для Сессии II.
    Удерживает строго изолированный хэш конкретной массы без ROOT и перекрестных ссылок.
    """
    raw_hash = hashlib.md5(text_seed.encode("utf-8")).hexdigest()
    numeric_seed = int(raw_hash, 16) % 100000
    random.seed(numeric_seed)
    
    viewbox_w = mediator_w * 3.7795
    viewbox_h = mediator_h * 3.7795
    
    svg_elements = []
    center_x_mm = mediator_w / 2.0
    center_y_mm = mediator_h / 2.0
    
    # СЛОЙ 1: Laser_Cut_External - КРАСНЫЙ (Внешний рез паспарту/медиатора)
    svg_elements.append(f'<rect x="0" y="0" width="{viewbox_w:.3f}" height="{viewbox_h:.3f}" fill="none" stroke="#ff0000" stroke-width="1.0" />')
    
    # СЛОЙ 2: Laser_Cut_Internal - ЗЕЛЕНЫЙ (Внутреннее окно портала изъятия)
    int_x = (center_x_mm - (visible_w / 2.0)) * 3.7795
    int_y = (center_y_mm - (visible_h / 2.0)) * 3.7795
    int_w = visible_w * 3.7795
    int_h = visible_h * 3.7795
    svg_elements.append(f'<rect x="{int_x:.3f}" y="{int_y:.3f}" width="{int_w:.3f}" height="{int_h:.3f}" fill="none" stroke="#00ff00" stroke-width="1.0" />')
    
    # СЛОЙ 3: Laser_Engrave_Hashes - СИНИЙ (Абсолютная изоляция крипто-паспорта)
    txt_x = center_x_mm * 3.7795
    txt_y = (center_y_mm + (visible_h / 2.0) + 6.0) * 3.7795
    
    # Стерильный синтаксис: только одна целевая метка без усечений и без ROOT_HASH
    ledger_string = f"LEDGER_ID // {label_prefix}: {target_id}"
    text_tag = f'<text x="{txt_x:.3f}" y="{txt_y:.3f}" font-family="monospace" font-size="3.5" font-weight="bold" text-anchor="middle" fill="#0000ff">{ledger_string}</text>'
    svg_elements.append(text_tag)
    
    # СЛОЙ 4: Laser_Engrave_Wave - ЧЕРНЫЙ (Интерференционный волновой шрам)
    start_x = center_x_mm - (visible_w / 2.0)
    end_x = center_x_mm + (visible_w / 2.0)
    
    y1_pixel = int_y
    y2_pixel = int_y + int_h
    
    steps = 1400
    for i in range(steps):
        t = -1.0 + (2.0 * i / (steps - 1))
        factor = math.sin(t * math.pi * 4.0) * math.exp(-t * t * 2.5)
        
        noise = random.uniform(-0.02, 0.02)
        offset_x = t * (visible_w / 2.0) + (factor * 3.5) + noise
        current_x = center_x_mm + offset_x
        
        if start_x <= current_x <= end_x:
            x_pixel = current_x * 3.7795
            line_tag = f'<line x1="{x_pixel:.3f}" y1="{y1_pixel:.3f}" x2="{x_pixel:.3f}" y2="{y2_pixel:.3f}" stroke="#000000" stroke-width="0.35" />'
            svg_elements.append(line_tag)

    svg_content = f'<svg xmlns="http://w3.org" viewBox="0 0 {viewbox_w:.1f} {viewbox_h:.1f}" width="{mediator_w}mm" height="{mediator_h}mm" style="background-color:#ffffff;">\n'
    svg_content += "\n".join(svg_elements)
    svg_content += "\n</svg>"
    
    # Вычисление относительного пути окружения для защиты OPSEC на GitHub
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(base_dir, "output_cnc", filename)
    
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
        print(f"SUCCESS: Deployed safely via relative vector path -> output_cnc/{filename}")
        return True
    except Exception as e:
        print(f"WRITE ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== INITIALIZING CNC FIXED EXTERNAL INTERFERENCE GENERATOR ===")
    
    hash_screen_s2 = "4bc19b131aa76aa7b9d8392477ab6aa2be690acb71c443e002c3c1c4a4ed59fd"
    hash_matrix_s2 = "b9d8392477ab6aa2be690acb71c443e002c3c1c4a4ed59fd4bc19b131aa76aa7b"
    
    # 1. ГЕОМЕТРИЯ БАЗЫ СЕМАНТИКИ (Изолированный хэш BASE_SCREEN)
    generate_wave_interference_svg(
        text_seed=machine_responses[0], 
        filename="semantic_base_production.svg", 
        mediator_w=320.0, mediator_h=220.0, visible_w=180.0, visible_h=125.0, 
        label_prefix="BASE_SCREEN", target_id=hash_screen_s2
    )
    
    # 2. ГЕОМЕТРИЯ ЯДРА СЕМАНТИКИ (Изолированный хэш CORE_MATRIX)
    generate_wave_interference_svg(
        text_seed=machine_responses[1], 
        filename="semantic_core_production.svg", 
        mediator_w=190.0, mediator_h=135.0, visible_w=130.0, visible_h=70.0, 
        label_prefix="CORE_MATRIX", target_id=hash_matrix_s2
    )
    print("=======================================================")
