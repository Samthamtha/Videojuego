import pygame
import sys
from pathlib import Path

# ================== RUTAS ROBUSTAS ==================
# Carpeta donde está este .py
BASE_DIR = Path(__file__).resolve().parent
IMG_DIR = BASE_DIR / "img"

def load_image(name, size=None, *, convert_alpha=True, fallback_color=(255, 0, 255, 180)):
    """
    Carga una imagen desde IMG_DIR/name. Si no existe o falla, devuelve una Surface de respaldo.
    name: str (nombre del archivo, p. ej., 'oso_R.png')
    size: (w, h) para escalar; si None, deja tamaño original
    convert_alpha: True para PNG con transparencia, False para fondos
    fallback_color: RGBA del cuadro sustituto si falla
    """
    try:
        surf = pygame.image.load(str(IMG_DIR / name))
        surf = surf.convert_alpha() if convert_alpha else surf.convert()
        if size:
            surf = pygame.transform.scale(surf, size)
        return surf
    except (pygame.error, FileNotFoundError) as e:
        print(f"ADVERTENCIA: no se pudo cargar '{name}': {e}")
        w, h = size if size else (120, 120)
        fb = pygame.Surface((w, h), pygame.SRCALPHA)
        fb.fill(fallback_color)
        return fb

# ================== PAUSA (OPCIONAL) ==================
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

# ================== CONSTANTES Y COLORES ==================
BLANCO = (255, 255, 255)
GRIS_CLARO = (200, 200, 200)
VERDE_REPARACION = (100, 180, 100)
ROJO_ROTO = (180, 50, 50)
AZUL_HERRAMIENTA = (50, 50, 180)  # Color original de fondo para herramientas
AMARILLO_SELECCION = (255, 255, 0)
AZUL_FONDO = (30, 144, 255)
NARANJA_TIEMPO = (255, 140, 0)
ROJO_VIDA = (255, 0, 0)

# --- Colores para flash de éxito ---
VERDE_TRANSPARENTE = (0, 200, 0, 100)

# --- Colores de fondos de herramientas ---
COLOR_FONDO_HERRAMIENTA = (70, 70, 70)
COLOR_BORDE_HERRAMIENTA = (150, 150, 150)

ANCHO = 1540
ALTO = 785
screen = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Nivel 2: Reparación con Teclado")
fuente = pygame.font.Font(None, 48)
clock = pygame.time.Clock()
FPS = 60

# ================== MEDIDAS DE ICONOS ==================
TOOL_DISPLAY_WIDTH = 120    # Caja (incluye fondo)
TOOL_DISPLAY_HEIGHT = 120
TOOL_IMG_WIDTH = 90         # Tamaño de la imagen interna
TOOL_IMG_HEIGHT = 90

# ================== CARGA DE HERRAMIENTAS ==================
HERRAMIENTAS_IMGS = {}
# Cargar y escalar todas las imágenes EXCEPTO "Liga" (que es un fallback)
HERRAMIENTAS_IMGS["Martillo"]  = load_image("Martillo.png",  (int(TOOL_IMG_WIDTH*1.2), int(TOOL_IMG_HEIGHT*1.2)))
HERRAMIENTAS_IMGS["Pegamento"] = load_image("Pegamento.png", (TOOL_IMG_WIDTH, TOOL_IMG_HEIGHT))
HERRAMIENTAS_IMGS["Lija"]      = load_image("Lija.png",      (TOOL_IMG_WIDTH, TOOL_IMG_HEIGHT))
HERRAMIENTAS_IMGS["Tornillos"] = load_image("Tornillos.png", (TOOL_IMG_WIDTH, TOOL_IMG_HEIGHT))
HERRAMIENTAS_IMGS["Pintura"]   = load_image("Pintura.png",   (TOOL_IMG_WIDTH, TOOL_IMG_HEIGHT))
HERRAMIENTAS_IMGS["Trapo"]     = load_image("Trapo.png",     (TOOL_IMG_WIDTH, TOOL_IMG_HEIGHT))
HERRAMIENTAS_IMGS["Clavos"]    = load_image("Clavos.png",    (TOOL_IMG_WIDTH, TOOL_IMG_HEIGHT))
# "Liga" no tiene imagen: se usará fallback azul en la clase Herramienta

# ================== DEFINICIÓN DE ETAPAS ==================
HERRAMIENTAS_NOMBRES = ["Martillo", "Pegamento", "Lija", "Tornillos", "Pintura", "Trapo", "Clavos", "Liga"]

OBJETOS = [
    "Osito de Peluche Roto",
    "Silla Rota",
    "Figura de Madera Rota"
]

# Herramientas necesarias por objeto (en orden)
REPARACION_ETAPAS = [
    ["Pegamento"],                 # 0. Osito
    ["Tornillos", "Martillo"],     # 1. Silla
    ["Pegamento", "Liga", "Pintura"]  # 2. Figura madera
]

# Solo nombres de archivos (no rutas completas)
OBJETO_IMAGENES = {
    "Osito de Peluche Roto": {
        "roto": "oso_R.png",
        "reparado": "oso_N.png"
    },
    "Silla Rota": {
        "roto": "silla_R.png",
        "reparado": "silla_N.png"
    },
    "Figura de Madera Rota": {
        "roto": "figura_maderaR.png",
        "reparado": "figura_madera.png"
    }
}

OBJETOS_IMGS_LOADED = {}  # superficies cargadas y escaladas

# ================== CLASE HERRAMIENTA ==================
class Herramienta(pygame.sprite.Sprite):
    """Representa una herramienta de reparación."""
    def __init__(self, x, y, ancho, alto, nombre):
        super().__init__()
        self.nombre = nombre
        self.seleccionada = False

        # Superficie principal con fondo y borde
        self.image = pygame.Surface([ancho, alto], pygame.SRCALPHA)
        self.image.fill(COLOR_FONDO_HERRAMIENTA)
        pygame.draw.rect(self.image, COLOR_BORDE_HERRAMIENTA, self.image.get_rect(), 3)

        # Imagen específica
        tool_img = HERRAMIENTAS_IMGS.get(nombre)
        if tool_img:
            img_x = (ancho - tool_img.get_width()) // 2
            img_y = (alto - tool_img.get_height()) // 2
            self.image.blit(tool_img, (img_x, img_y))
        else:
            # Fallback (Liga)
            temp_surface = pygame.Surface([TOOL_IMG_WIDTH, TOOL_IMG_HEIGHT], pygame.SRCALPHA)
            temp_surface.fill(AZUL_HERRAMIENTA)
            img_x = (ancho - TOOL_IMG_WIDTH) // 2
            img_y = (alto - TOOL_IMG_HEIGHT) // 2
            self.image.blit(temp_surface, (img_x, img_y))

        self.rect = self.image.get_rect(topleft=(x, y))

# ================== FONDO ==================
FONDO_NIVEL2 = load_image("pibble_fondo.png", (ANCHO, ALTO), convert_alpha=False, fallback_color=(30,144,255,255))

# ================== NIVEL 2 ==================
def run_level2(dificultad, idioma, screen):
    global ANCHO, ALTO, fuente, clock, FPS, FONDO_NIVEL2, OBJETO_IMAGENES, OBJETOS_IMGS_LOADED

    # Cargar imágenes de objetos una sola vez
    if not OBJETOS_IMGS_LOADED:
        OBJETO_DISPLAY_SIZE = (300, 300)
        for obj_name, paths in OBJETO_IMAGENES.items():
            OBJETOS_IMGS_LOADED[obj_name] = {}
            for state, filename in paths.items():
                color = ROJO_ROTO if state == "roto" else VERDE_REPARACION
                OBJETOS_IMGS_LOADED[obj_name][state] = load_image(
                    filename, OBJETO_DISPLAY_SIZE, fallback_color=(*color, 200)
                )

    # --- Estado del juego ---
    vidas = 3
    tiempo_total = 60.0
    tiempo_restante = tiempo_total
    objeto_actual_index = 0
    etapa_actual = 0
    mensaje_feedback = ""
    mensaje_timer = 0.0
    objeto_reparado_timer = 0.0
    success_flash_timer = 0.0
    juego_finalizado = False

    # --- UI herramientas (2 columnas a la derecha) ---
    tool_ancho = TOOL_DISPLAY_WIDTH
    tool_alto = TOOL_DISPLAY_HEIGHT
    gap = 20
    herramientas_list = []

    num_herramientas = len(HERRAMIENTAS_NOMBRES)  # 8
    num_columnas = 2
    num_filas = num_herramientas // num_columnas  # 4

    x_offset = 50
    x_start_col2 = ANCHO - x_offset - tool_ancho
    x_start_col1 = ANCHO - x_offset - (2 * tool_ancho + gap)
    TOTAL_HEIGHT = (num_filas * tool_alto) + ((num_filas - 1) * gap)
    y_start = (ALTO - TOTAL_HEIGHT) // 2

    for i in range(num_herramientas):
        nombre = HERRAMIENTAS_NOMBRES[i]
        x = x_start_col1 if i % 2 == 0 else x_start_col2
        y = y_start + (i // 2) * (tool_alto + gap)
        herramientas_list.append(Herramienta(x, y, tool_ancho, tool_alto, nombre))

    index_seleccionado = 0
    herramientas_list[index_seleccionado].seleccionada = True

    running = True
    while running:
        delta_time = clock.tick(FPS) / 1000.0

        if not juego_finalizado:
            # Flash éxito
            if success_flash_timer > 0:
                success_flash_timer -= delta_time
                if success_flash_timer < 0:
                    success_flash_timer = 0.0

            # Cronómetro (no durante la pausa por reparación)
            if objeto_reparado_timer == 0.0:
                tiempo_restante -= delta_time

            if tiempo_restante <= 0:
                tiempo_restante = 0
                juego_finalizado = True
                mensaje_feedback = "¡TIEMPO AGOTADO!"

            # Mensajes temporales
            if mensaje_timer > 0:
                mensaje_timer -= delta_time
                if mensaje_timer <= 0:
                    mensaje_feedback = ""

            # Pausa de objeto reparado (4s)
            if objeto_reparado_timer > 0:
                objeto_reparado_timer -= delta_time
                if objeto_reparado_timer <= 0:
                    objeto_reparado_timer = 0.0
                    objeto_actual_index += 1
                    etapa_actual = 0
                    if objeto_actual_index >= len(OBJETOS):
                        juego_finalizado = True
                        mensaje_feedback = "¡NIVEL COMPLETADO! "
                        mensaje_timer = 3.0
                    else:
                        mensaje_feedback = f"Continúa con: {OBJETOS[objeto_actual_index]}"
                        mensaje_timer = 2.0

            if vidas <= 0 and not juego_finalizado:
                juego_finalizado = True
                mensaje_feedback = "¡SIN VIDAS! JUEGO TERMINADO"

            # Eventos
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    return "salir_juego"

                elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                    accion = mostrar_menu_pausa(screen, ALTO, ANCHO)
                    if accion == "reiniciar":
                        return "reiniciar"
                    elif accion == "salir":
                        return "salir_menu"

                elif evento.type == pygame.KEYDOWN and not juego_finalizado and objeto_reparado_timer == 0.0:
                    # Deselecciona actual
                    herramientas_list[index_seleccionado].seleccionada = False

                    # Movimiento vertical
                    if evento.key in (pygame.K_s, pygame.K_DOWN):
                        if index_seleccionado + 2 < len(herramientas_list):
                            index_seleccionado = index_seleccionado + 2
                        else:
                            index_seleccionado = (index_seleccionado + 1) % len(herramientas_list)
                    elif evento.key in (pygame.K_w, pygame.K_UP):
                        if index_seleccionado - 2 >= 0:
                            index_seleccionado = index_seleccionado - 2
                        else:
                            index_seleccionado = (index_seleccionado - 1) % len(herramientas_list)

                    # Movimiento horizontal
                    elif evento.key in (pygame.K_d, pygame.K_RIGHT):
                        if index_seleccionado % 2 == 0:
                            index_seleccionado = (index_seleccionado + 1) % len(herramientas_list)
                    elif evento.key in (pygame.K_a, pygame.K_LEFT):
                        if index_seleccionado % 2 != 0:
                            index_seleccionado = (index_seleccionado - 1) % len(herramientas_list)

                    index_seleccionado = index_seleccionado % len(herramientas_list)
                    herramientas_list[index_seleccionado].seleccionada = True

                    # Usar herramienta (ENTER)
                    if evento.key == pygame.K_RETURN:
                        herramienta_usada = herramientas_list[index_seleccionado].nombre
                        if objeto_actual_index < len(OBJETOS):
                            herramientas_necesarias = REPARACION_ETAPAS[objeto_actual_index]
                            if etapa_actual >= len(herramientas_necesarias):
                                continue
                            herramienta_correcta_actual = herramientas_necesarias[etapa_actual]

                            if herramienta_usada == herramienta_correcta_actual:
                                # Correcto
                                etapa_actual += 1
                                success_flash_timer = 0.5
                                if etapa_actual >= len(herramientas_necesarias):
                                    # Objeto completo
                                    objeto_reparado_timer = 4.0
                                    mensaje_feedback = "¡OBJETO REPARADO! Esperando 4 segundos..."
                                    mensaje_timer = 4.0
                                else:
                                    siguiente_tool = herramientas_necesarias[etapa_actual]
                                    mensaje_feedback = f"¡Herramienta '{herramienta_usada}' CORRECTA! Siguiente: {siguiente_tool}"
                                    mensaje_timer = 2.0
                            else:
                                # Incorrecto
                                vidas -= 1
                                mensaje_feedback = f"HERRAMIENTA INCORRECTA: Se resta 1 vida. (Vidas restantes: {vidas})"
                                mensaje_timer = 2.0

        # ================== DIBUJO ==================
        # Fondo
        if FONDO_NIVEL2:
            screen.blit(FONDO_NIVEL2, (0, 0))
        else:
            screen.fill(AZUL_FONDO)

        # Área de trabajo central (semi-transparente)
        area_trabajo_surface = pygame.Surface((ANCHO // 2, int(ALTO * 0.75)), pygame.SRCALPHA)
        area_trabajo_surface.fill((*GRIS_CLARO, 180))
        area_trabajo_rect = area_trabajo_surface.get_rect(topleft=(ANCHO // 4, ALTO // 8))
        screen.blit(area_trabajo_surface, area_trabajo_rect.topleft)

        # Rect del objeto
        objeto_display_size = (300, 300)
        objeto_roto_rect = pygame.Rect(
            area_trabajo_rect.centerx - objeto_display_size[0] // 2,
            area_trabajo_rect.centery - objeto_display_size[1] // 2,
            objeto_display_size[0],
            objeto_display_size[1]
        )

        # Título
        texto_titulo = fuente.render("Nivel 2: VAMOS A REPARAR", True, BLANCO)
        screen.blit(texto_titulo, (ANCHO // 2 - texto_titulo.get_width() // 2, 20))

        # Vidas
        texto_vidas = fuente.render(f"Vidas: {vidas} ", True, ROJO_VIDA)
        screen.blit(texto_vidas, (50, 20))

        # Barra de tiempo
        BARRA_TIEMPO_ANCHO = ANCHO // 3
        BARRA_TIEMPO_ALTO = 20
        x_barra_tiempo = ANCHO // 2 - BARRA_TIEMPO_ANCHO // 2
        y_barra_tiempo = 70
        pygame.draw.rect(screen, ROJO_ROTO, (x_barra_tiempo, y_barra_tiempo, BARRA_TIEMPO_ANCHO, BARRA_TIEMPO_ALTO), 3)
        progreso_ancho = int((tiempo_restante / tiempo_total) * BARRA_TIEMPO_ANCHO)
        if objeto_reparado_timer > 0.0 and tiempo_restante > 0:
            progreso_ancho = int((tiempo_restante / tiempo_total) * BARRA_TIEMPO_ANCHO)
        pygame.draw.rect(screen, NARANJA_TIEMPO, (x_barra_tiempo, y_barra_tiempo, progreso_ancho, BARRA_TIEMPO_ALTO))
        texto_tiempo = pygame.font.Font(None, 30).render(f"Tiempo: {int(tiempo_restante)}s", True, BLANCO)
        screen.blit(texto_tiempo, (x_barra_tiempo + BARRA_TIEMPO_ANCHO + 10, y_barra_tiempo))

        # Objeto actual
        objeto_actual_nombre = OBJETOS[objeto_actual_index] if objeto_actual_index < len(OBJETOS) else "¡TERMINADO!"
        texto_objeto = fuente.render(f"OBJETO: {objeto_actual_nombre}", True, AZUL_HERRAMIENTA)
        screen.blit(texto_objeto, (ANCHO // 2 - texto_objeto.get_width() // 2, area_trabajo_rect.top + 20))

        # Caja de pista (izquierda)
        CAJA_PISTA_ANCHO = 250
        CAJA_PISTA_ALTO = 150
        x_pista = 50
        y_pista = ALTO // 2 - CAJA_PISTA_ALTO // 2
        pygame.draw.rect(screen, GRIS_CLARO, (x_pista, y_pista, CAJA_PISTA_ANCHO, CAJA_PISTA_ALTO), 0)
        pygame.draw.rect(screen, BLANCO, (x_pista, y_pista, CAJA_PISTA_ANCHO, CAJA_PISTA_ALTO), 3)
        texto_pista_titulo = pygame.font.Font(None, 30).render("HERRAMIENTA REQUERIDA", True, AZUL_HERRAMIENTA)
        screen.blit(texto_pista_titulo, (x_pista + CAJA_PISTA_ANCHO // 2 - texto_pista_titulo.get_width() // 2, y_pista + 10))

        # Contenido de pista
        if not juego_finalizado and objeto_actual_index < len(OBJETOS) and objeto_reparado_timer == 0.0:
            herramientas_necesarias = REPARACION_ETAPAS[objeto_actual_index]
            pista_tool_nombre = herramientas_necesarias[etapa_actual]
            pista_tool_img = HERRAMIENTAS_IMGS.get(pista_tool_nombre)
            if pista_tool_img:
                scaled_img = pygame.transform.scale(pista_tool_img, (80, 80))
                img_pista_x = x_pista + CAJA_PISTA_ANCHO // 2 - scaled_img.get_width() // 2
                img_pista_y = y_pista + 50
                screen.blit(scaled_img, (img_pista_x, img_pista_y))
            else:
                texto_pista_contenido = fuente.render(pista_tool_nombre, True, ROJO_ROTO)
                screen.blit(texto_pista_contenido, (x_pista + CAJA_PISTA_ANCHO // 2 - texto_pista_contenido.get_width() // 2, y_pista + 50))
        elif objeto_reparado_timer > 0.0:
            texto_pista_contenido = fuente.render("REPARADO", True, VERDE_REPARACION)
            screen.blit(texto_pista_contenido, (x_pista + CAJA_PISTA_ANCHO // 2 - texto_pista_contenido.get_width() // 2, y_pista + 50))
        else:
            texto_pista_contenido = pygame.font.Font(None, 30).render("FIN DEL JUEGO", True, ROJO_ROTO)
            screen.blit(texto_pista_contenido, (x_pista + CAJA_PISTA_ANCHO // 2 - texto_pista_contenido.get_width() // 2, y_pista + 50))

        # Dibujar herramientas (derecha)
        for herramienta in herramientas_list:
            if herramienta.seleccionada and objeto_reparado_timer == 0.0:
                pygame.draw.rect(screen, AMARILLO_SELECCION, herramienta.rect.inflate(10, 10), 5)
            screen.blit(herramienta.image, herramienta.rect)
            texto_nombre = pygame.font.Font(None, 24).render(herramienta.nombre, True, BLANCO)
            screen.blit(texto_nombre, (herramienta.rect.x + 5, herramienta.rect.y + 5))

        # Dibuja objeto (roto o reparado)
        if objeto_actual_index < len(OBJETOS) and OBJETOS[objeto_actual_index] in OBJETO_IMAGENES:
            obj_name = OBJETOS[objeto_actual_index]
            if objeto_reparado_timer > 0.0:
                image_key = "reparado"
            elif juego_finalizado and objeto_actual_index == len(OBJETOS) - 1:
                image_key = "reparado"
            else:
                image_key = "roto"
            img_to_draw = OBJETOS_IMGS_LOADED[obj_name][image_key]
            screen.blit(img_to_draw, objeto_roto_rect.topleft)

        # Flash de éxito
        if success_flash_timer > 0.0:
            flash_surface = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            flash_surface.fill(VERDE_TRANSPARENTE)
            screen.blit(flash_surface, (0, 0))

        # Mensaje de estado (abajo)
        if objeto_reparado_timer > 0.0:
            estado_texto = f"OBJETO REPARADO! Siguiente objeto en {int(objeto_reparado_timer) + 1} segundos..."
            color_estado = VERDE_REPARACION
        elif mensaje_feedback:
            estado_texto = mensaje_feedback
            color_estado = ROJO_ROTO if ("INCORRECTA" in mensaje_feedback or "AGOTADO" in mensaje_feedback or "SIN VIDAS" in mensaje_feedback) \
                           else VERDE_REPARACION
        elif juego_finalizado:
            estado_texto = mensaje_feedback
            color_estado = ROJO_ROTO if vidas <= 0 or tiempo_restante <= 0 else VERDE_REPARACION
        else:
            estado_texto = "Presiona ENTER para usar la herramienta seleccionada"
            color_estado = BLANCO

        texto_estado = fuente.render(estado_texto, True, color_estado)
        screen.blit(texto_estado, (ANCHO // 2 - texto_estado.get_width() // 2, ALTO - 60))

        pygame.display.flip()

    return "finalizado"

# ================== EJECUCIÓN ==================
if __name__ == '__main__':
    accion = "iniciar"
    while accion != "salir_juego":
        if accion in ("iniciar", "reiniciar"):
            accion = run_level2(dificultad=1, idioma="es", screen=screen)
        elif accion == "salir_menu":
            accion = "salir_juego"

    pygame.quit()
    sys.exit()
