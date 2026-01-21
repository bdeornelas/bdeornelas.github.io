#!/usr/bin/env python3
"""
Script per croppare la foto del dottore in modo molto più stretto
Rimuove spazio sopra la testa e taglia dalle spalle in giù
"""

from PIL import Image
import os

# Percorsi
input_path = "../assets/img/benjamin-de-ornelas-portrait.jpg"
output_path = "../assets/img/benjamin-de-ornelas-portrait-cropped.jpg"

# Carica l'immagine
img = Image.open(input_path)
width, height = img.size

print(f"Dimensioni originali: {width}x{height}")

# Crop molto più aggressivo:
# - Rimuovi il 10% superiore (spazio sopra la testa)
# - Rimuovi il 45% inferiore (dalle spalle in giù, incluse le mani)
# Questo lascia solo il 45% centrale che include viso, collo e parte alta del camice

top_crop = int(height * 0.10)  # Inizia dal 10% dall'alto
bottom_crop = int(height * 0.55)  # Finisce al 55% (rimuove il 45% inferiore)

cropped_img = img.crop((0, top_crop, width, bottom_crop))

print(f"Dimensioni croppate: {cropped_img.size}")
print(f"Rimosso {top_crop}px dall'alto e {height - bottom_crop}px dal basso")

# Salva l'immagine croppata
cropped_img.save(output_path, quality=95, optimize=True)
print(f"Immagine salvata in: {output_path}")
