# menu.py
import pygame
import sys
import os

from settings import config_menu, idioma, dificultad

# FUNCIÓN: carga todos los frames desde una carpeta
def cargar_frames_desde_carpeta(carpeta):
    frames = []
    if not os.path.exists(carpeta):
        print(f"⚠️ Carpeta no encontrada: {carpeta}")
        return frames

    for archivo in sorted(os.listdir(carpeta)):
        if archivo.endswith((".png", ".jpg")):
            ruta = os.path.join(carpeta, archivo)
            imagen = pygame.image.load(ruta).convert_alpha()
            frames.append(imagen)

    print(f" {len(frames)} frames cargados desde {carpeta}")
    return frames



def credits_menu(screen):
    font = pygame.font.SysFont(None, 40)
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return

        screen.fill((255, 255, 255))
        title = font.render("CRÉDITOS", True, (0,0,0))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 50))

        text1 = font.render("Juego desarrollado por:", True, (0,0,0))
        text2 = font.render("Tu Nombre Aquí", True, (200,0,0))
        screen.blit(text1, (screen.get_width()//2 - text1.get_width()//2, 200))
        screen.blit(text2, (screen.get_width()//2 - text2.get_width()//2, 260))

        back_text = font.render("Presiona ENTER para volver", True, (0,0,0))
        screen.blit(back_text, (screen.get_width()//2 - back_text.get_width()//2, 500))

        pygame.display.flip()
        clock.tick(60)

def run_menu(screen, dificultad, idioma):
    font = pygame.font.SysFont(None, 48)
    clock = pygame.time.Clock()
    main_menu_options = ["Iniciar Juego", "Configuración", "Créditos", "Salir"]
    selected_option = 0

    # fondo
    fondo = pygame.image.load("img/fondoinicio.png").convert()
    fondo = pygame.transform.scale(fondo, (screen.get_width(), screen.get_height()))

    # Cargar frames desde tus carpetas reales
    frames_iniciar = cargar_frames_desde_carpeta("img/frames_iniciar")
    frames_config = cargar_frames_desde_carpeta("img/frames_configuracion")
    frames_creditos = cargar_frames_desde_carpeta("img/frames_creditos")
    frames_salir = cargar_frames_desde_carpeta("img/frames_salir")

    frame_index = 0
    frame_timer = 0


    # Cargar la imagen del título
    titulo_img = pygame.image.load("img/logo.png").convert_alpha()  # PNG transparente
    # Ajustar tamaño
    titulo_img = pygame.transform.scale(titulo_img, (600, 300))  # ancho x alto deseado


    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(main_menu_options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(main_menu_options)
                elif event.key == pygame.K_RETURN:
                    opcion = main_menu_options[selected_option]
                    if opcion == "Iniciar Juego":
                        return "jugar", dificultad, idioma
                    elif opcion == "Configuración":
                        config_menu(screen)
                    elif opcion == "Créditos":
                        credits_menu(screen)
                    elif opcion == "Salir":
                        return "salir", dificultad, idioma
                    

        #🔁 Animar cada 5 ticks
        frame_timer += 1
        if frame_timer >= 5:
            frame_index = (frame_index + 1) % 1000
            frame_timer = 0


        # Dibujar menú
        screen.blit(fondo, (0, 0))
        rect_titulo = titulo_img.get_rect(center=(screen.get_width()//2, 100))  # posición Y deseada
        screen.blit(titulo_img, rect_titulo)

        # Función para mostrar cada botón con su animación
        def mostrar_boton(frames, texto, y, seleccionado=False, ancho=200, alto=80):   

            if seleccionado:
                 # Cargar PNG especial para seleccionado
                 ruta_png = f"img/{texto.lower().replace(' ','_')}_selected.png"
                 if os.path.exists(ruta_png):
                     img = pygame.image.load(ruta_png).convert_alpha()
                     img = pygame.transform.scale(img, (ancho, alto))
                     rect = img.get_rect(center=(screen.get_width()//2, y))
                     screen.blit(img, rect)
                     return  # ya dibujamos, no necesitamos más

            if frames:
                # Escalar frame al tamaño deseado
                img = pygame.transform.scale(frames[frame_index % len(frames)], (ancho, alto))
                rect = img.get_rect(center=(screen.get_width()//2, y))
                screen.blit(img, rect)
            else:
                color = (200,0,0) if texto == main_menu_options[selected_option] else (0,0,0)
                text = font.render(texto, True, color)
                rect = text.get_rect(center=(screen.get_width()//2, y))
                screen.blit(text, rect)


        # Mostrar cada botón (posición Y ajustable)
        mostrar_boton(frames_iniciar, "Iniciar Juego", 250, seleccionado=(selected_option==0))
        mostrar_boton(frames_config, "Configuración", 350, seleccionado=(selected_option==1))
        mostrar_boton(frames_creditos, "Créditos", 450, seleccionado=(selected_option==2))
        mostrar_boton(frames_salir, "Salir", 550, seleccionado=(selected_option==3))


       #for i, option in enumerate(main_menu_options):
       #    color = (200,0,0) if i == selected_option else (0,0,0)
       #    text = font.render(option, True, color)
       #    screen.blit(text, (screen.get_width()//2 - text.get_width()//2, 200 + i*60))

        pygame.display.flip()
        clock.tick(60)
