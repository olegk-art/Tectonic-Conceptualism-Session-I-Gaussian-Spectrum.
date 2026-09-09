# -*- coding: utf-8 -*-
import os

def generate_semantic_spin_rotated_phantom(filename, stone_w=150.0, stone_h=110.0, phantom_w=130.0, phantom_h=70.0):
    """
    Генератор ЧПУ-карт Матрицы спинов Сессии II [ЭЛЕМЕНТ M_006].
    Полная маскировка путей и приведение к синтаксису LEDGER_ID.
    """
    viewbox_w = stone_w * 3.7795
    viewbox_h = stone_h * 3.7795
    
    svg_elements = []
    
    # СЛОЙ 1: Laser_Cut_External - Внешний габарит камня 150х110 мм (КРАСНЫЙ)
    w_str = f"{viewbox_w:.3f}"
    h_str = f"{viewbox_h:.3f}"
    ext_rect = '<rect x="0" y="0" width="' + w_str + '" height="' + h_str + '" fill="none" stroke="#ff0000" stroke-width="1.0" />'
    svg_elements.append(ext_rect)
    
    # СЛОЙ 2: Laser_Engrave_Phantom - Развернутый фантом окна Ядра на 90 градусов (ЗЕЛЕНЫЙ)
    center_x = viewbox_w / 2.0
    center_y = viewbox_h / 2.0
    ph_w_px = phantom_w * 3.7795
    ph_h_px = phantom_h * 3.7795
    ph_x = center_x - (ph_w_px / 2.0)
    ph_y = center_y - (ph_h_px / 2.0)
    
    x_str = f"{ph_x:.3f}"
    y_str = f"{ph_y:.3f}"
    pw_str = f"{ph_w_px:.3f}"
    ph_str = f"{ph_h_px:.3f}"
    phantom_rect = '<rect x="' + x_str + '" y="' + y_str + '" width="' + pw_str + '" height="' + ph_str + '" fill="none" stroke="#00ff00" stroke-width="1.0" />'
    svg_elements.append(phantom_rect)
    
    # СЛОЙ 3: Laser_Engrave_Hashes - Автоматическое клеймение полных кодов в формате LEDGER_ID (СИНИЙ)
    t1_x = center_x
    t1_y = (center_y + (ph_h_px / 2.0) + 8.0)
    
    h1_str = "LEDGER_ID // BASE_SCREEN: 4bc19b131aa76aa7b9d8392477ab6aa2be690acb71c443e002c3c1c4a4ed59fd"
    text_tag1 = '<text x="' + f"{t1_x:.3f}" + '" y="' + f"{t1_y:.3f}" + '" font-family="monospace" font-size="3.5" font-weight="bold" text-anchor="middle" fill="#0000ff">' + h1_str + '</text>'
    svg_elements.append(text_tag1)
    
    t2_y = t1_y + 5.0
    h2_str = "LEDGER_ID // CORE_MATRIX: b9d8392477ab6aa2be690acb71c443e002c3c1c4a4ed59fd4bc19b131aa76aa7b"
    text_tag2 = '<text x="' + f"{t1_x:.3f}" + '" y="' + f"{t2_y:.3f}" + '" font-family="monospace" font-size="3.5" font-weight="bold" text-anchor="middle" fill="#0000ff">' + h2_str + '</text>'
    svg_elements.append(text_tag2)
    
    # Сборка финального XML/SVG файла
    svg_content = '<svg xmlns="http://w3.org" viewBox="0 0 ' + f"{viewbox_w:.1f} {viewbox_h:.1f}" + '" width="' + str(stone_w) + 'mm" height="' + str(stone_h) + 'mm" style="background-color:#ffffff;">\n'
    svg_content += "  <!-- SYSTEM_ROTATED_SPIN_LOCK -->\n"
    svg_content += "\n".join(svg_elements)
    svg_content += "\n运行 </svg>"
    
    # Изоляция путей файловой системы ЭВМ
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(base_dir, "output_cnc", filename)
    
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
        print("SUCCESS: Deployed safely via relative vector path -> output_cnc/" + filename)
        return True
    except Exception as e:
        print("WRITE ERROR: " + str(e))
        return False

if __name__ == "__main__":
    print("=== INITIALIZING CNC ROTATED SPIN PHANTOM GENERATOR ===")
    # Фантомы окон и хэши приведены к прецизионным раздельным контурам
    generate_semantic_spin_rotated_phantom(filename="semantic_spin_phantom.svg", stone_w=150.0, stone_h=110.0, phantom_w=130.0, phantom_h=70.0)
    print("=======================================================")
