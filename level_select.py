# level_select.py
import pygame
import sys

# La función debe recibir dificultad e idioma para mantener la consistencia con main.py
def run_level_select(screen, dificultad, idioma): 
    # Aseguramos que Pygame.font.init() esté llamado si es necesario, 
    # aunque main.py ya llama a pygame.init()
    if not pygame.font.get_init():
        pygame.font.init() 
        
    font = pygame.font.SysFont(None, 40)
    clock = pygame.time.Clock()

    selected_option = 0
    options = ["Nivel 1", "Nivel 2", "Nivel 3", "Volver"]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Si cierra, salimos del juego
                return "salir_juego", dificultad, idioma 
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    opcion = options[selected_option]
                    
                    if "Nivel" in opcion:
                        # *** PARADA CLAVE: DETENER MÚSICA DE MENÚ ANTES DE ENTRAR AL NIVEL ***
                        pygame.mixer.music.stop() 
                        # Retorna el nivel seleccionado para que main.py inicie la música específica
                        return opcion, dificultad, idioma 
                    
                    elif opcion == "Volver":
                        # Retorna al menú. La música del menú sigue sonando (no la detenemos).
                        return "menu", dificultad, idioma 
                        
        
        # Dibuja
        screen.fill((255, 255, 255))
        title = font.render("SELECCIONA EL NIVEL", True, (0,0,0))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 50))

        for i, option in enumerate(options):
            color = (200,0,0) if i == selected_option else (0,0,0)
            text = font.render(option, True, color)
            screen.blit(text, (screen.get_width()//2 - text.get_width()//2, 200 + i*50))

        pygame.display.flip()
        clock.tick(60)

    # Si por alguna razón el bucle se rompe, retorna al menú
    return "menu", dificultad, idioma