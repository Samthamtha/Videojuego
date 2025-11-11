# level2.py
import pygame
import sys
# Asegúrate de que 'pause.py' existe
try:
    from pause import mostrar_menu_pausa 
except ImportError:
    # Función dummy de respaldo si el archivo 'pause.py' no se encuentra
    def mostrar_menu_pausa(screen, ALTO, ANCHO):
        print("ADVERTENCIA: 'pause.py' no encontrado. Presiona cualquier tecla para reanudar.")
        pygame.time.wait(500)
        return "reanudar" 

pygame.init()

#CONSTANTES Y COLORES
BLANCO = (255, 255, 255)
GRIS_CLARO = (200, 200, 200)
VERDE_REPARACION = (100, 180, 100)
ROJO_ROTO = (180, 50, 50) 
AZUL_HERRAMIENTA = (50, 50, 180) # Color original de fondo para herramientas
AMARILLO_SELECCION = (255, 255, 0)
AZUL_FONDO = (30, 144, 255)
NARANJA_TIEMPO = (255, 140, 0)
ROJO_VIDA = (255, 0, 0)

# --- NUEVOS COLORES PARA LOS FONDOS DE LAS HERRAMIENTAS ---
COLOR_FONDO_HERRAMIENTA = (70, 70, 70) # Un gris oscuro para el fondo de cada herramienta
COLOR_BORDE_HERRAMIENTA = (150, 150, 150) # Un gris más claro para el borde

ANCHO = 1540
ALTO = 785
screen = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Nivel 2: Reparación con Teclado")
fuente = pygame.font.Font(None, 48)
clock = pygame.time.Clock() 
FPS = 60

# --- 🛠️ MODIFICACIÓN 1: Cargar y Escalar Imágenes de Herramientas ---

# Tamaño del área total para cada herramienta, incluyendo el fondo
TOOL_DISPLAY_WIDTH = 120 # Más grande para el fondo
TOOL_DISPLAY_HEIGHT = 120 # Más grande para el fondo

# Tamaño real de la imagen de la herramienta dentro de su fondo
TOOL_IMG_WIDTH = 90 # Martillo, Pegamento, etc., serán de este tamaño
TOOL_IMG_HEIGHT = 90 # Martillo, Pegamento, etc., serán de este tamaño

HERRAMIENTAS_IMGS = {}
# Nota: Asume que las imágenes están en una carpeta 'img/'
try:
    # Cargar y escalar todas las imágenes EXCEPTO "Liga"
    # Ajustamos el tamaño del martillo para que sea proporcionalmente más grande si es necesario
    HERRAMIENTAS_IMGS["Martillo"] = pygame.image.load("img/Martillo.png").convert_alpha()
    HERRAMIENTAS_IMGS["Martillo"] = pygame.transform.scale(HERRAMIENTAS_IMGS["Martillo"], (int(TOOL_IMG_WIDTH * 1.2), int(TOOL_IMG_HEIGHT * 1.2))) # Martillo un poco más grande
    
    HERRAMIENTAS_IMGS["Pegamento"] = pygame.image.load("img/Pegamento.png").convert_alpha()
    HERRAMIENTAS_IMGS["Pegamento"] = pygame.transform.scale(HERRAMIENTAS_IMGS["Pegamento"], (TOOL_IMG_WIDTH, TOOL_IMG_HEIGHT))
    
    HERRAMIENTAS_IMGS["Lija"] = pygame.image.load("img/Lija.png").convert_alpha()
    HERRAMIENTAS_IMGS["Lija"] = pygame.transform.scale(HERRAMIENTAS_IMGS["Lija"], (TOOL_IMG_WIDTH, TOOL_IMG_HEIGHT))
    
    HERRAMIENTAS_IMGS["Tornillos"] = pygame.image.load("img/Tornillos.png").convert_alpha()
    HERRAMIENTAS_IMGS["Tornillos"] = pygame.transform.scale(HERRAMIENTAS_IMGS["Tornillos"], (TOOL_IMG_WIDTH, TOOL_IMG_HEIGHT))
    
    HERRAMIENTAS_IMGS["Pintura"] = pygame.image.load("img/Pintura.png").convert_alpha()
    HERRAMIENTAS_IMGS["Pintura"] = pygame.transform.scale(HERRAMIENTAS_IMGS["Pintura"], (TOOL_IMG_WIDTH, TOOL_IMG_HEIGHT))
    
    HERRAMIENTAS_IMGS["Trapo"] = pygame.image.load("img/Trapo.png").convert_alpha()
    HERRAMIENTAS_IMGS["Trapo"] = pygame.transform.scale(HERRAMIENTAS_IMGS["Trapo"], (TOOL_IMG_WIDTH, TOOL_IMG_HEIGHT))
    
    HERRAMIENTAS_IMGS["Clavos"] = pygame.image.load("img/Clavos.png").convert_alpha()
    HERRAMIENTAS_IMGS["Clavos"] = pygame.transform.scale(HERRAMIENTAS_IMGS["Clavos"], (TOOL_IMG_WIDTH, TOOL_IMG_HEIGHT))
    
    # Imagen de respaldo para "Liga" si no la tienes o si falla la carga
    HERRAMIENTAS_IMGS["Liga"] = pygame.Surface([TOOL_IMG_WIDTH, TOOL_IMG_HEIGHT], pygame.SRCALPHA)
    HERRAMIENTAS_IMGS["Liga"].fill(AZUL_HERRAMIENTA) # Usa el color de respaldo
    
except pygame.error as e:
    print(f"ADVERTENCIA: No se pudo cargar una o más imágenes de herramientas. {e}")
    # Si alguna carga falla, se usará el color de fondo como respaldo.

# DEFINICIÓN DE ETAPAS DEL JUEGO

HERRAMIENTAS_NOMBRES = ["Martillo", "Pegamento", "Lija", "Tornillos", "Pintura", "Trapo", "Clavos", "Liga"] 

OBJETOS = [
    "Osito de Peluche Roto",
    "Silla Rota",
    "Figura de Madera Rota"
]

# Definición de las etapas de reparación para cada objeto: HERRAMIENTAS NECESARIAS EN ORDEN
REPARACION_ETAPAS = [
    ["Pegamento"], # 0. Osito de Peluche: Pegamento
    ["Tornillos", "Martillo"], # 1. Silla Rota: TORNILLOS, luego Martillo
    ["Pegamento", "Liga", "Pintura"] # 2. Figura de Madera: Pegamento, Liga, Pintura
]


# Clase Herramienta
class Herramienta(pygame.sprite.Sprite):
    """Representa una herramienta de reparación."""
    # --- 🛠️ MODIFICACIÓN 2: Usar la imagen cargada y añadir un fondo ---
    def __init__(self, x, y, ancho, alto, nombre):
        super().__init__()
        self.nombre = nombre
        self.seleccionada = False

        # Superficie principal que contendrá el fondo y la imagen de la herramienta
        self.image = pygame.Surface([ancho, alto], pygame.SRCALPHA) # Permite transparencia
        self.image.fill(COLOR_FONDO_HERRAMIENTA) # Rellena con el color de fondo

        # Dibuja un borde para la herramienta
        pygame.draw.rect(self.image, COLOR_BORDE_HERRAMIENTA, self.image.get_rect(), 3)

        # Cargar la imagen específica para esta herramienta
        tool_img = HERRAMIENTAS_IMGS.get(nombre)
        
        if tool_img:
            # Calcular la posición para centrar la imagen dentro del fondo
            img_x = (ancho - tool_img.get_width()) // 2
            img_y = (alto - tool_img.get_height()) // 2
            self.image.blit(tool_img, (img_x, img_y))
        else:
            # Fallback si no hay imagen (solo debería pasar con 'Liga' si no tiene imagen)
            temp_surface = pygame.Surface([TOOL_IMG_WIDTH, TOOL_IMG_HEIGHT], pygame.SRCALPHA)
            temp_surface.fill(AZUL_HERRAMIENTA)
            img_x = (ancho - TOOL_IMG_WIDTH) // 2
            img_y = (alto - TOOL_IMG_HEIGHT) // 2
            self.image.blit(temp_surface, (img_x, img_y))


        self.rect = self.image.get_rect(topleft=(x, y))

# --- 🖼️ MODIFICACIÓN 4: Cargar Imagen de Fondo (Fuera de run_level2 para cargar solo una vez) ---
try:
    FONDO_NIVEL2 = pygame.image.load("img/pibble_fondo.png").convert()
    # Escalar la imagen para que coincida con el tamaño de la pantalla
    FONDO_NIVEL2 = pygame.transform.scale(FONDO_NIVEL2, (ANCHO, ALTO))
except pygame.error as e:
    print(f"ERROR: No se pudo cargar la imagen de fondo 'img/pibble_fondo.png'. {e}")
    FONDO_NIVEL2 = None
# ---------------------------------------------------------------------------------------------------


# Función principal del Nivel 2
def run_level2():
    global ANCHO, ALTO, screen, fuente, clock, FPS, FONDO_NIVEL2

    #Variables de Estado del Juego
    vidas = 3
    tiempo_total = 60.0 # 60 segundos
    tiempo_restante = tiempo_total
    
    objeto_actual_index = 0
    # etapa_actual es el índice de la herramienta requerida en REPARACION_ETAPAS[objeto_actual_index]
    etapa_actual = 0 
    
    mensaje_feedback = "" # Mensaje temporal para mostrar feedback al jugador
    mensaje_timer = 0.0 # Contador para desaparecer el mensaje después de un tiempo
    
    # --- TEMPORIZADOR PARA MOSTRAR EL OBJETO REPARADO (4 segundos) ---
    objeto_reparado_timer = 0.0 
    
    juego_finalizado = False
    
    # Usar las constantes definidas globalmente para el tamaño de la herramienta
    tool_ancho = TOOL_DISPLAY_WIDTH 
    tool_alto = TOOL_DISPLAY_HEIGHT
    gap = 20 # Espacio entre herramientas
    
    herramientas_list = []
    
    #LÓGICA DE POSICIONAMIENTO DE HERRAMIENTAS (2 Columnas a la Derecha)
    num_herramientas = len(HERRAMIENTAS_NOMBRES) # 8 herramientas
    num_columnas = 2
    num_filas = num_herramientas // num_columnas # 4 filas

    # Posiciones X (Dos columnas a la Derecha)
    x_offset = 50 # Margen derecho
    x_start_col2 = ANCHO - x_offset - tool_ancho 
    x_start_col1 = ANCHO - x_offset - (2 * tool_ancho + gap) 
    
    # Posición Y, centrado verticalmente
    TOTAL_HEIGHT = (num_filas * tool_alto) + ((num_filas - 1) * gap)
    y_start = (ALTO - TOTAL_HEIGHT) // 2 
    
    # Llenar la lista de herramientas
    for i in range(num_herramientas):
        nombre = HERRAMIENTAS_NOMBRES[i]
        
        # Columna 1 (indices 0, 2, 4, 6)
        if i % 2 == 0:
            x = x_start_col1
        # Columna 2 (indices 1, 3, 5, 7)
        else:
            x = x_start_col2
            
        # Fila (i // 2 da el número de fila: 0, 1, 2, 3)
        y = y_start + (i // 2) * (tool_alto + gap)
            
        herramientas_list.append(Herramienta(x, y, tool_ancho, tool_alto, nombre))

    # Área de visualización del objeto (Central)
    objeto_roto_rect = pygame.Rect(ANCHO // 2 - 150, ALTO // 2 - 150, 300, 300) 
    
    index_seleccionado = 0
    herramientas_list[index_seleccionado].seleccionada = True

    #bucle Principal del Juego
    running = True
    while running:
        # delta_time: Tiempo en segundos desde el último frame
        delta_time = clock.tick(FPS) / 1000.0 
        
        #Lógica de Tiempo y Fin de Juego
        if not juego_finalizado:
            
            # <<<< MODIFICADO POR PAUSA DE TIEMPO >>>>
            # Solo decrementa el tiempo restante si NO estamos en la pausa de objeto reparado
            if objeto_reparado_timer == 0.0:
                tiempo_restante -= delta_time
            # <<<< MODIFICADO POR PAUSA DE TIEMPO >>>>
            
            if tiempo_restante <= 0:
                tiempo_restante = 0
                juego_finalizado = True
                mensaje_feedback = "¡TIEMPO AGOTADO!"
            
            # Timer para mensajes temporales
            if mensaje_timer > 0:
                mensaje_timer -= delta_time
                if mensaje_timer <= 0:
                    mensaje_feedback = ""
            
            # --- LÓGICA DE 4 SEGUNDOS: TEMPORIZADOR DE OBJETO REPARADO ---
            if objeto_reparado_timer > 0:
                objeto_reparado_timer -= delta_time
                
                if objeto_reparado_timer <= 0:
                    # El tiempo ha terminado, avanzar al siguiente objeto
                    objeto_reparado_timer = 0.0 # Asegurar que es 0
                    objeto_actual_index += 1
                    etapa_actual = 0 # Reiniciar etapa para el nuevo objeto
                    
                    if objeto_actual_index >= len(OBJETOS):
                          # ¡NIVEL TERMINADO!
                          juego_finalizado = True
                          mensaje_feedback = "¡NIVEL COMPLETADO! "
                          mensaje_timer = 3.0
                    else:
                          # Mensaje de transición al nuevo objeto
                          mensaje_feedback = f"Continúa con: {OBJETOS[objeto_actual_index]}"
                          mensaje_timer = 2.0 
            
            if vidas <= 0 and not juego_finalizado:
                juego_finalizado = True
                mensaje_feedback = "¡SIN VIDAS! JUEGO TERMINADO"
            
            # Bucle de Eventos
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    return "salir_juego" 
                
                # Manejo del Menú de Pausa (Escape)
                elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                    accion = mostrar_menu_pausa(screen, ALTO, ANCHO) 
                    
                    if accion == "reiniciar":
                        return "reiniciar" 
                    elif accion == "salir":
                        return "salir_menu" 

                # Manejo del Teclado para Movimiento y Acción (Solo si el juego no ha terminado Y NO ESTAMOS EN PAUSA POR REPARACIÓN)
                elif evento.type == pygame.KEYDOWN and not juego_finalizado and objeto_reparado_timer == 0.0:
                    
                    #deseleccionar herramienta actual
                    herramientas_list[index_seleccionado].seleccionada = False
                    
                    # Movimiento Vertical (W/S o Flechas UP/DOWN)
                    if evento.key == pygame.K_s or evento.key == pygame.K_DOWN:
                        # Lógica para moverse a la siguiente fila/columna 
                        if index_seleccionado + 2 < len(herramientas_list):
                            index_seleccionado = index_seleccionado + 2
                        else:
                            # Si no hay dos, va a la siguiente (e.g., de 6 a 7, o de 7 a 0)
                            index_seleccionado = (index_seleccionado + 1) % len(herramientas_list)
                            
                    elif evento.key == pygame.K_w or evento.key == pygame.K_UP:
                        # Lógica para moverse a la fila/columna anterior
                        if index_seleccionado - 2 >= 0:
                            index_seleccionado = index_seleccionado - 2
                        else:
                            # Si no hay dos, va a la anterior (e.g., de 0 a 7, o de 1 a 0)
                            index_seleccionado = (index_seleccionado - 1) % len(herramientas_list)

                    
                    # Movimiento Horizontal (A/D o Flechas LEFT/RIGHT)
                    elif evento.key == pygame.K_d or evento.key == pygame.K_RIGHT:
                        if index_seleccionado % 2 == 0: # Si estoy en columna 1 (0, 2, 4, 6)
                            index_seleccionado = (index_seleccionado + 1) % len(herramientas_list) 
                    elif evento.key == pygame.K_a or evento.key == pygame.K_LEFT:
                        if index_seleccionado % 2 != 0: # Si estoy en columna 2 (1, 3, 5, 7)
                            index_seleccionado = (index_seleccionado - 1) % len(herramientas_list)
                    
                    # Asegurar que el índice esté dentro de los límites
                    index_seleccionado = index_seleccionado % len(herramientas_list)
                    
                    #seleccionar nueva herramienta
                    herramientas_list[index_seleccionado].seleccionada = True

                    #LÓGICA DE REPARACIÓN (ENTER)
                    if evento.key == pygame.K_RETURN:
                        herramienta_usada = herramientas_list[index_seleccionado].nombre
                        
                        # Chequea si quedan objetos por reparar
                        if objeto_actual_index < len(OBJETOS):
                            herramientas_necesarias = REPARACION_ETAPAS[objeto_actual_index]
                            
                            # Maneja el caso en que la etapa actual ya no existe (objeto terminado)
                            if etapa_actual >= len(herramientas_necesarias):
                                continue

                            herramienta_correcta_actual = herramientas_necesarias[etapa_actual]

                            if herramienta_usada == herramienta_correcta_actual:
                                # HERRAMIENTA CORRECTA: AVANZA A LA SIGUIENTE ETAPA
                                etapa_actual += 1
                                
                                if etapa_actual >= len(herramientas_necesarias):
                                    # OBJETO REPARADO COMPLETAMENTE: INICIAR TEMPORIZADOR DE 4 SEGUNDOS
                                    
                                    objeto_reparado_timer = 4.0 
                                    
                                    mensaje_feedback = "¡OBJETO REPARADO! Esperando 4 segundos..."
                                    mensaje_timer = 4.0 # El mensaje dura lo mismo que la pausa
                                    
                                else:
                                    # ETAPA INTERMEDIA COMPLETADA
                                    siguiente_tool = herramientas_necesarias[etapa_actual]
                                    mensaje_feedback = f"¡Herramienta '{herramienta_usada}' CORRECTA! Siguiente: {siguiente_tool}"
                                    mensaje_timer = 2.0
                                    
                            else:
                                # HERRAMIENTA INCORRECTA: DEDUCIR VIDA
                                vidas -= 1
                                mensaje_feedback = f"HERRAMIENTA INCORRECTA: Se resta 1 vida. (Vidas restantes: {vidas})"
                                mensaje_timer = 2.0 
                                
        # Dibujo y Renderizado
        
        # --- 🖼️ MODIFICACIÓN 5: Dibujar la Imagen de Fondo (Antes de todo) ---
        if FONDO_NIVEL2:
            screen.blit(FONDO_NIVEL2, (0, 0))
        else:
            # Fallback si no hay imagen de fondo
            screen.fill(AZUL_FONDO)
        # ----------------------------------------------------------------------
        
        # Dibuja el Área de trabajo (Fondo central)
        # Haremos que el área de trabajo sea semi-transparente para que se vea el fondo
        area_trabajo_surface = pygame.Surface((ANCHO // 2, ALTO * 0.75), pygame.SRCALPHA)
        area_trabajo_surface.fill((*GRIS_CLARO, 180)) # Color gris claro con 180 de opacidad (0-255)
        area_trabajo_rect = area_trabajo_surface.get_rect(topleft=(ANCHO // 4, ALTO // 8))
        screen.blit(area_trabajo_surface, area_trabajo_rect.topleft)
        # Ahora el objeto_roto_rect se calcula en base al área de trabajo para que esté centrado
        objeto_roto_rect = pygame.Rect(area_trabajo_rect.centerx - 150, area_trabajo_rect.centery - 150, 300, 300) 
        
        # Dibujar Título
        texto_titulo = fuente.render("Nivel 2: VAMOS A REPARAR", True, BLANCO)
        screen.blit(texto_titulo, (ANCHO // 2 - texto_titulo.get_width() // 2, 20)) 
        
        #UI Lateral (Parte Superior)
        
        # 1. Vidas
        texto_vidas = fuente.render(f"Vidas: {vidas} ", True, ROJO_VIDA)
        screen.blit(texto_vidas, (50, 20)) 
        
        # 2. Barra de Tiempo
        BARRA_TIEMPO_ANCHO = ANCHO // 3
        BARRA_TIEMPO_ALTO = 20
        x_barra_tiempo = ANCHO // 2 - BARRA_TIEMPO_ANCHO // 2
        y_barra_tiempo = 70
        
        #fondo y borde de la barra
        pygame.draw.rect(screen, ROJO_ROTO, (x_barra_tiempo, y_barra_tiempo, BARRA_TIEMPO_ANCHO, BARRA_TIEMPO_ALTO), 3)
        
        #fontenido de la barra (progreso)
        progreso_ancho = int((tiempo_restante / tiempo_total) * BARRA_TIEMPO_ANCHO)
        
        # <<<< MODIFICADO POR PAUSA DE TIEMPO >>>>
        # Si el tiempo está detenido, aseguramos que la barra refleje el tiempo_restante sin decrecer
        if objeto_reparado_timer > 0.0 and tiempo_restante > 0:
              # Si el juego está en pausa, aseguramos que la barra se mantiene
              progreso_ancho = int((tiempo_restante / tiempo_total) * BARRA_TIEMPO_ANCHO)
        # <<<< MODIFICADO POR PAUSA DE TIEMPO >>>>

        pygame.draw.rect(screen, NARANJA_TIEMPO, (x_barra_tiempo, y_barra_tiempo, progreso_ancho, BARRA_TIEMPO_ALTO))
        
        #Texto de tiempo restante
        texto_tiempo = pygame.font.Font(None, 30).render(f"Tiempo: {int(tiempo_restante)}s", True, BLANCO)
        screen.blit(texto_tiempo, (x_barra_tiempo + BARRA_TIEMPO_ANCHO + 10, y_barra_tiempo))
        
        #Panel de Objeto Actual (dentro del área de trabajo)
        objeto_actual_nombre = OBJETOS[objeto_actual_index] if objeto_actual_index < len(OBJETOS) else "¡TERMINADO!"
        
        texto_objeto = fuente.render(f"OBJETO: {objeto_actual_nombre}", True, AZUL_HERRAMIENTA)
        screen.blit(texto_objeto, (ANCHO // 2 - texto_objeto.get_width() // 2, area_trabajo_rect.top + 20))

        #caja de Pista que esta situado en la parte izquierda de la pantalla
        CAJA_PISTA_ANCHO = 250
        CAJA_PISTA_ALTO = 150
        x_pista = 50
        y_pista = ALTO // 2 - CAJA_PISTA_ALTO // 2

        # mostrar el cuadro
        pygame.draw.rect(screen, GRIS_CLARO, (x_pista, y_pista, CAJA_PISTA_ANCHO, CAJA_PISTA_ALTO), 0)
        pygame.draw.rect(screen, BLANCO, (x_pista, y_pista, CAJA_PISTA_ANCHO, CAJA_PISTA_ALTO), 3)

        # Contenido de la pista
        texto_pista_titulo = pygame.font.Font(None, 30).render("HERRAMIENTA REQUERIDA", True, AZUL_HERRAMIENTA)
        screen.blit(texto_pista_titulo, (x_pista + CAJA_PISTA_ANCHO // 2 - texto_pista_titulo.get_width() // 2, y_pista + 10))
        
        # Mostrar la pista si el juego no ha terminado y quedan objetos Y NO ESTÁ EN PAUSA
        if not juego_finalizado and objeto_actual_index < len(OBJETOS) and objeto_reparado_timer == 0.0:
            herramientas_necesarias = REPARACION_ETAPAS[objeto_actual_index]
            pista_tool_nombre = herramientas_necesarias[etapa_actual] # Obtenemos el nombre de la herramienta

            # --- 🛠️ MODIFICACIÓN 3: Dibujar la imagen de la herramienta requerida ---
            pista_tool_img = HERRAMIENTAS_IMGS.get(pista_tool_nombre)

            if pista_tool_img:
                # Calculamos un tamaño más pequeño para la imagen en la pista
                PISTA_IMG_WIDTH = 80
                PISTA_IMG_HEIGHT = 80
                scaled_img = pygame.transform.scale(pista_tool_img, (PISTA_IMG_WIDTH, PISTA_IMG_HEIGHT))
                
                # Posiciona la imagen centrada debajo del título de la pista
                img_pista_x = x_pista + CAJA_PISTA_ANCHO // 2 - scaled_img.get_width() // 2
                img_pista_y = y_pista + 50 # Un poco más abajo que el título
                screen.blit(scaled_img, (img_pista_x, img_pista_y))
                
                # Si quieres, puedes omitir el texto de la pista si la imagen ya lo representa
                # texto_pista_contenido = fuente.render(pista_tool_nombre, True, ROJO_ROTO)
                # screen.blit(texto_pista_contenido, (x_pista + CAJA_PISTA_ANCHO // 2 - texto_pista_contenido.get_width() // 2, y_pista + 50))
            else:
                # Si no hay imagen (ej. Liga, o si falla la carga), mostrar solo el texto
                texto_pista_contenido = fuente.render(pista_tool_nombre, True, ROJO_ROTO)
                screen.blit(texto_pista_contenido, (x_pista + CAJA_PISTA_ANCHO // 2 - texto_pista_contenido.get_width() // 2, y_pista + 50))
            
        elif objeto_reparado_timer > 0.0:
              # Muestra la pista de "REPARADO" durante la pausa
              texto_pista_contenido = fuente.render("REPARADO", True, VERDE_REPARACION)
              screen.blit(texto_pista_contenido, (x_pista + CAJA_PISTA_ANCHO // 2 - texto_pista_contenido.get_width() // 2, y_pista + 50))
        else:
            # mensaje cuando el juego finaliza o se completa
            texto_pista_contenido = pygame.font.Font(None, 30).render("FIN DEL JUEGO", True, ROJO_ROTO)
            screen.blit(texto_pista_contenido, (x_pista + CAJA_PISTA_ANCHO // 2 - texto_pista_contenido.get_width() // 2, y_pista + 50))


        # Dibujar las Herramientas en la parte derecha
        for i, herramienta in enumerate(herramientas_list):
            
            # Dibujar el borde de selección solo si no hay pausa activa
            # El rect.inflate(10, 10) hará el borde 5px más grande por cada lado
            if herramienta.seleccionada and objeto_reparado_timer == 0.0:
                pygame.draw.rect(screen, AMARILLO_SELECCION, herramienta.rect.inflate(10, 10), 5) # Borde más grueso
            
            # --- Aquí se dibuja la imagen de la herramienta (que ahora incluye su fondo) ---
            screen.blit(herramienta.image, herramienta.rect)
            
            # Dibujar el nombre de la herramienta (superpuesto en la imagen, ajustado para no cubrir mucho)
            texto_nombre = pygame.font.Font(None, 24).render(herramienta.nombre, True, BLANCO)
            # Posiciona el texto del nombre en la parte superior izquierda de la casilla de la herramienta
            screen.blit(texto_nombre, (herramienta.rect.x + 5, herramienta.rect.y + 5))

        # mostrar Objeto Roto / Reparado 
        
        if juego_finalizado or objeto_actual_index >= len(OBJETOS) or objeto_reparado_timer > 0.0:
            color_objeto = VERDE_REPARACION # Verde si ya terminó, el nivel se completó, o si está en el temporizador
        elif etapa_actual > 0:
            color_objeto = VERDE_REPARACION # Verde si ya se usó al menos una herramienta correcta
        else:
            color_objeto = ROJO_ROTO # Rojo si está en la primera etapa
            
        pygame.draw.rect(screen, color_objeto, objeto_roto_rect, 0)
        
        # Mensaje de estado que esta situado en la parte inferior central
        estado_texto = ""
        color_estado = BLANCO
        
        if objeto_reparado_timer > 0.0:
              # Si el objeto está en pausa, mostrar el tiempo restante de pausa
              # Usamos int(objeto_reparado_timer) + 1 para que cuente 4, 3, 2, 1...
              estado_texto = f"OBJETO REPARADO! Siguiente objeto en {int(objeto_reparado_timer) + 1} segundos..."
              color_estado = VERDE_REPARACION
        elif mensaje_feedback:
            estado_texto = mensaje_feedback
            color_estado = ROJO_ROTO if "INCORRECTA" in mensaje_feedback or "AGOTADO" in mensaje_feedback or "SIN VIDAS" in mensaje_feedback else VERDE_REPARACION
        elif juego_finalizado:
              estado_texto = mensaje_feedback
              color_estado = ROJO_ROTO if vidas <= 0 or tiempo_restante <= 0 else VERDE_REPARACION
        else:
            estado_texto = "Presiona ENTER para usar la herramienta seleccionada"
            
        texto_estado = fuente.render(estado_texto, True, color_estado)
        screen.blit(texto_estado, (ANCHO // 2 - texto_estado.get_width() // 2, ALTO - 60))
        
        # Actualizar la pantalla
        pygame.display.flip()

    return "finalizado"

# esto es la ejecución del Juego 
if __name__ == '__main__':
    accion = "iniciar"
    while accion != "salir_juego":
        
        if accion == "iniciar" or accion == "reiniciar":
            accion = run_level2()
        
        elif accion == "salir_menu":
            # Aquí se asume que volvería al menú principal
            accion = "salir_juego" 

    pygame.quit()
    sys.exit()