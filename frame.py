from PIL import Image
import os

def extraer_frames_gif(ruta_gif, carpeta_salida):
    gif = Image.open(ruta_gif)
    os.makedirs(carpeta_salida, exist_ok=True)
    frame = 0
    while True:
        frame_path = os.path.join(carpeta_salida, f"frame_{frame}.png")
        gif.save(frame_path, "PNG")
        frame += 1
        try:
            gif.seek(frame)
        except EOFError:
            break
    print(f" {frame} frames extraídos en '{carpeta_salida}'")

# Ejemplo (hazlo con cada botón)
extraer_frames_gif("img/iniciar.gif", "img/frames_iniciar")
extraer_frames_gif("img/configuracion.gif", "img/frames_configuracion")
extraer_frames_gif("img/creditos.gif", "img/frames_creditos")
extraer_frames_gif("img/salir.gif", "img/frames_salir")
