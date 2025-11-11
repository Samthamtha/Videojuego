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
LEVEL1_MUSIC = 'sonido/musica_nivel1.mp3' # AJUSTAR RUTA
LEVEL2_MUSIC = 'sonido/musica_nivel2.mp3' # AJUSTAR RUTA
LEVEL3_MUSIC = 'sonido/musica_nivel3.mp3' # AJUSTAR RUTA

def play_music(file_path, volume=0.3, loop=-1):
    """Carga y reproduce una pista de música, deteniendo la anterior."""
    try:
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        
        # Verifica si el archivo es diferente al actual antes de cargar, si es necesario
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(loop)
        
    except pygame.error as e:
        print(f"Advertencia: No se pudo cargar o reproducir la música '{file_path}'. Error: {e}")


def main():
    pygame.init()
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
            # Si se viene de un nivel, volvemos a poner la música del menú/selección
            play_music(MENU_MUSIC)
            reiniciar_musica_menu = False 

        accion_global = None 

        accion_menu, dificultad, idioma = run_menu(screen, dificultad, idioma)

        if accion_menu == "jugar":
            # Selección de nivel: La música del menú SIGUE SONANDO aquí.
            nivel_seleccionado, dificultad, idioma = run_level_select(screen, dificultad, idioma)
            
            # Si el usuario selecciona "Volver" en level_select.py, retorna "menu"
            if nivel_seleccionado == "menu":
                 continue 
                 
            # Si el usuario selecciona un nivel, run_level_select ya DETUVO la música.
            
            nivel = nivel_seleccionado 
            
            # Bucle interno para manejar Reinicio o Salida de un nivel
            while True:
                accion_nivel = None 
                musica_a_tocar = None

                # 2. INICIAR MÚSICA DEL NIVEL Y LLAMAR AL NIVEL
                if nivel == "Nivel 3":
                    musica_a_tocar = LEVEL3_MUSIC
                    play_music(musica_a_tocar) 
                    accion_nivel = run_level3(dificultad, idioma, screen)
                
                elif nivel == "Nivel 2": 
                    musica_a_tocar = LEVEL2_MUSIC
                    play_music(musica_a_tocar) 
                    accion_nivel = run_level2()
                
                elif nivel == "Nivel 1":
                    musica_a_tocar = LEVEL1_MUSIC
                    play_music(musica_a_tocar) 
                    accion_nivel = run_level1(dificultad, idioma, screen)
                
                else:
                    # En caso de error o retorno inesperado
                    reiniciar_musica_menu = True
                    break 
                
                
                # LÓGICA POST-NIVEL (Salida/Reinicio)
                
                if accion_nivel == "reiniciar":
                    # Detener y continuar al inicio del while True para que se vuelva a llamar a play_music(musica_a_tocar)
                    pygame.mixer.music.stop() 
                    continue 

                elif accion_nivel == "salir_menu":
                    # Sale del nivel para volver a la selección de nivel (bucle externo)
                    pygame.mixer.music.stop() # Detener música del nivel
                    reiniciar_musica_menu = True # La bandera indica que se debe volver a poner la música del menú
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