# main.py
import pygame
import sys
from menu import run_menu 
from level_select import run_level_select 
from level1 import run_level1
from level2 import run_level2
from level3 import run_level3

# CONSTANTES DE MÚSICA - AJUSTA ESTAS RUTAS
MENU_MUSIC = 'sonido/inicio_musica.mp3'
LEVEL1_MUSIC = 'sonido/musica_nivel1.mp3'  # AJUSTAR RUTA
LEVEL2_MUSIC = 'sonido/musica_nivel2.mp3'  # AJUSTAR RUTA
LEVEL3_MUSIC = 'sonido/musica_nivel3.mp3'  # AJUSTAR RUTA

# Mapeo de claves de niveles (coinciden con los return_key del level_select.py)
LEVEL_MAP = {
    "level1": {"music": LEVEL1_MUSIC, "function": run_level1},
    "level2": {"music": LEVEL2_MUSIC, "function": run_level2},
    "level3": {"music": LEVEL3_MUSIC, "function": run_level3},
}


def play_music(file_path, volume=0.3, loop=-1):
    """Carga y reproduce una pista de música, deteniendo la anterior."""
    try:
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        
        # Carga la música
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(loop)
        
    except pygame.error as e:
        print(f"Advertencia: No se pudo cargar o reproducir la música '{file_path}'. Error: {e}")


def main():
    # Inicialización de Pygame
    pygame.init()
    
    # Aseguramos la inicialización explícita del mixer para música
    try:
        pygame.mixer.init()
    except pygame.error as e:
        print(f"Advertencia: No se pudo inicializar el mezclador de sonido. {e}")

    ANCHO = 1540
    ALTO = 785
    screen = pygame.display.set_mode((ANCHO, ALTO)) 
    pygame.display.set_caption("Juego del Río")

    dificultad = "Normal"
    idioma = "Español"
    
    # 1. INICIAMOS LA MÚSICA DEL MENÚ AL PRINCIPIO
    play_music(MENU_MUSIC) 
    
    # Bandera para saber si necesitamos reiniciar la música del menú
    reiniciar_musica_menu = False 

    while True:
        
        # LÓGICA DE REINICIO DE MÚSICA DEL MENÚ
        if reiniciar_musica_menu:
            play_music(MENU_MUSIC)
            reiniciar_musica_menu = False 

        accion_global = None 

        accion_menu, dificultad, idioma = run_menu(screen, dificultad, idioma)

        if accion_menu == "jugar":
            # Selección de nivel: La música del menú SIGUE SONANDO aquí.
            nivel_seleccionado, dificultad, idioma = run_level_select(screen, dificultad, idioma)
            
            # Si el usuario selecciona "Volver"
            if nivel_seleccionado == "menu":
                 continue 
                 
            nivel = nivel_seleccionado 
            
            # Bucle interno para manejar Reinicio o Salida de un nivel
            while True:
                accion_nivel = None 

                # --- NUEVO: ahora usamos el mapeo ---
                if nivel in LEVEL_MAP:
                    play_music(LEVEL_MAP[nivel]["music"])
                    accion_nivel = LEVEL_MAP[nivel]["function"](dificultad, idioma, screen)
                else:
                    print(f"ADVERTENCIA: Nivel '{nivel}' no mapeado. Volviendo al menú principal.")
                    reiniciar_musica_menu = True
                    break 
                
                # LÓGICA POST-NIVEL (Salida/Reinicio)
                if accion_nivel == "reiniciar":
                    pygame.mixer.music.stop() 
                    continue 

                elif accion_nivel == "salir_menu":
                    pygame.mixer.music.stop() 
                    reiniciar_musica_menu = True
                    break 
                
                elif accion_nivel == "salir_juego":
                    accion_global = "salir"
                    pygame.mixer.music.stop() 
                    break

            if accion_global == "salir":
                break

        elif accion_menu == "salir":
            break 
        
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
