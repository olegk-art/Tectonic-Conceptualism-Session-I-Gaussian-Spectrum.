# -*- coding: utf-8 -*-
import hashlib

TOTAL_WIDTH = 440.0
TOTAL_HEIGHT = 190.0

OFFSET_Y = 40.0 
PANEL_HEIGHT = 90.0

W1_X1, W1_X2 = 98.824, 172.941
W2_X1, W2_X2 = 182.941, 257.058
W3_X1, W3_X2 = 267.058, 341.175

final_core_hash = """02c3c1c4a4ed59fd4bc19b131aa76aa7b9d8392477ab6aa2be690acb71c443e0"""
final_screen_hash = """811bf9ed5df0de31f41360e5f15d4af8d8174eef405232792852101cd3cf9653"""


with open("spin_matrix_phantom.svg", "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="utf-8"?>\n')
    f.write(f'<svg version="1.1" xmlns="http://w3.org" width="{TOTAL_WIDTH}mm" height="{TOTAL_HEIGHT}mm" viewBox="0 0 {TOTAL_WIDTH} {TOTAL_HEIGHT}">\n')
    
    f.write('  <g id="Laser_Phantom_Frame" fill="none" stroke="#000000" stroke-width="0.15">\n')
    f.write(f'    <rect x="0.0" y="0.0" width="{TOTAL_WIDTH}" height="{TOTAL_HEIGHT}" />\n')
    f.write(f'    <rect x="{W1_X1}" y="{OFFSET_Y + 10.0}" width="74.117" height="{PANEL_HEIGHT}" />\n')
    f.write(f'    <rect x="{W2_X1}" y="{OFFSET_Y + 10.0}" width="74.117" height="{PANEL_HEIGHT}" />\n')
    f.write(f'    <rect x="{W3_X1}" y="{OFFSET_Y + 10.0}" width="74.117" height="{PANEL_HEIGHT}" />\n')
    f.write('  </g>\n')
    
    f.write(f'  <text x="{TOTAL_WIDTH / 2.0}" y="{TOTAL_HEIGHT - 5.0}" font-family="monospace" font-size="1.8" fill="#000000" text-anchor="middle">')
    f.write(f'LEDGER_ID // SCREEN: {final_screen_hash} // MATRIX: {final_core_hash}')
    f.write('</text>\n')
    
    f.write('</svg>')

print("=================== COMPILATION SUCCESSFUL ===================")
print("Файл Матрицы спинов 'spin_matrix_phantom.svg' успешно создан.")
print("==============================================================")
