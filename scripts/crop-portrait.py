#!/usr/bin/env python3
"""
Script per croppare la foto del dottore rimuovendo le mani
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

# Croppa l'immagine: rimuovi il 30% inferiore dove ci sono le mani
# Mantieni la parte superiore (dalla testa fino al petto, escludendo mani)
crop_height = int(height * 0.70)  # Mantieni il 70% superiore
cropped_img = img.crop((0, 0, width, crop_height))

print(f"Dimensioni croppate: {cropped_img.size}")

# Salva l'immagine croppata
cropped_img.save(output_path, quality=95, optimize=True)
print(f"Immagine salvata in: {output_path}")
