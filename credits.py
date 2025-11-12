import pygame, sys

WIDTH, HEIGHT = 1540, 785 

def show_credits(screen):
    clock = pygame.time.Clock()

    name_font = pygame.font.Font(None, 40)
    return_font = pygame.font.Font(None, 36)
    
    TEXT_COLOR = (0, 0, 0)
    BACKGROUND_COLOR = (255, 255, 255)

    
    equipo = [
        ("Sami", "Guzman.", "img/samiC.png"),
        ("Alvaro", "Guerrero.", "img/alvaroC.png"),
        ("Brian", "Sebastian.", "img/brianC.png"),
        ("Romario", "Vazquez.", "img/romarioC.png")
    ]

    img_width, img_height = 200, 200
    imagenes_cargadas = []
    
    for nombre, apellido, archivo in equipo:
        try:
            img = pygame.image.load(archivo).convert_alpha()
            img = pygame.transform.scale(img, (img_width, img_height))
            imagenes_cargadas.append(img)
        except pygame.error as e:
            print(f"Error al cargar imagen {archivo}: {e}")
            # Sustituto si la imagen falla
            placeholder_img = pygame.Surface((img_width, img_height), pygame.SRCALPHA)
            pygame.draw.circle(placeholder_img, (150, 150, 150), (img_width // 2, img_height // 2), img_width // 2 - 5, 0)
            pygame.draw.circle(placeholder_img, (255, 0, 0), (img_width // 2, img_height // 2), img_width // 2 - 5, 5)
            imagenes_cargadas.append(placeholder_img)

    #Bucle Principal de Créditos
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # Usamos ENTER para volver
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                return 

        screen.fill(BACKGROUND_COLOR) 

        #Distribución de los 4 Integrantes
        
        num_integrantes = len(equipo)
        spacing = 50 # Espacio entre cada elemento
        
        # Calcular el ancho total del bloque (4 imágenes + 3 espacios)
        total_content_width = (img_width * num_integrantes) + (spacing * (num_integrantes - 1))
        
        # Punto de inicio para centrar el bloque horizontalmente
        start_x = (WIDTH - total_content_width) // 2
        
        # Posición Y fija para todas las imágenes y nombres
        image_y = HEIGHT // 3 
        name_y = image_y + img_height + 15 

        current_x = start_x
        
        for i, (nombre, apellido, archivo) in enumerate(equipo):
            # mostrar la imagen
            screen.blit(imagenes_cargadas[i], (current_x, image_y))

            # mostrar nombres
            nombre_completo = f"{nombre} {apellido}"
            texto_nombre = name_font.render(nombre_completo, True, TEXT_COLOR)
            
            # Centrar el nombre bajo la imagen
            name_x = current_x + (img_width - texto_nombre.get_width()) // 2
            screen.blit(texto_nombre, (name_x, name_y))
            
            #Mover a la siguiente posición horizontal
            current_x += img_width + spacing 

        #Mensaje para Volver (Centrado Abajo)
        return_text = return_font.render("Presiona ENTER para volver", True, TEXT_COLOR)
        screen.blit(return_text, (WIDTH // 2 - return_text.get_width() // 2, HEIGHT - 60))

        pygame.display.flip()
        clock.tick(60)

#Para probar el archivo credits.py individualmente
if __name__ == "__main__":
    pygame.init()
    test_screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Créditos del Juego")
    show_credits(test_screen)
    pygame.quit()
    sys.exit()