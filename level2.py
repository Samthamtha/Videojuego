import pygame
import sys
import random
import math
from pathlib import Path
from pause import mostrar_menu_pausa
from victory_menu import mostrar_menu_victoria, mostrar_menu_derrota
# Import tutorial for level 2
from tutorial_nivel2 import mostrar_tutorial_nivel2
from translations import get_text

# ================== RUTAS ROBUSTAS ==================
BASE_DIR = Path(__file__).resolve().parent
IMG_DIR = BASE_DIR / "img"

def load_image(name, size=None, *, convert_alpha=True, fallback_color=(255, 0, 255, 180)):
    """Carga una imagen desde IMG_DIR/name. Si no existe o falla, devuelve una Surface de respaldo."""
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

pygame.init()

# ================== CONSTANTES Y COLORES ==================
BLANCO = (255, 255, 255)
GRIS_CLARO = (220, 220, 220)
VERDE_REPARACION = (80, 200, 120)
ROJO_ROTO = (220, 60, 60)
AZUL_HERRAMIENTA = (50, 80, 200)
AMARILLO_SELECCION = (255, 230, 0)
AZUL_FONDO = (30, 144, 255)
NARANJA_TIEMPO = (255, 160, 0)
ROJO_VIDA = (255, 50, 80)
VERDE_TRANSPARENTE = (0, 200, 0, 100)

# Color llamativo para el texto del tiempo
AMARILLO_TIEMPO_TEXTO = (255, 255, 0)

# Colores más vivos para las tarjetas
COLOR_FONDO_HERRAMIENTA = (40, 40, 80)
COLOR_BORDE_HERRAMIENTA = (255, 255, 255)

ANCHO = 1540
ALTO = 785
screen = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Nivel 2 - Taller de Reparaciones")
fuente = pygame.font.Font(None, 48)
clock = pygame.time.Clock()
FPS = 60

# ================== MEDIDAS DE ICONOS ==================
TOOL_DISPLAY_WIDTH = 130
TOOL_DISPLAY_HEIGHT = 130
TOOL_IMG_WIDTH = 90
TOOL_IMG_HEIGHT = 90

# ================== HELPERS DE DIBUJO ==================
def draw_rounded_rect(surface, color, rect, radius=20, width=0):
    pygame.draw.rect(surface, color, rect, width=width, border_radius=radius)

def render_text_shrink(text, max_width, color, base_size=28, min_size=14):
    """Renderiza texto ajustando tamaño para que no se salga del ancho máximo."""
    size = base_size
    last_surf = None
    while size >= min_size:
        font = pygame.font.Font(None, size)
        surf = font.render(text, True, color)
        if surf.get_width() <= max_width:
            return surf, font
        last_surf = surf
        size -= 2
    return last_surf, pygame.font.Font(None, min_size)

# ================== CARGA DE HERRAMIENTAS ==================
HERRAMIENTAS_IMGS = {}
HERRAMIENTAS_IMGS["Martillo"]  = load_image("Martillo.png",  (int(TOOL_IMG_WIDTH*1.2), int(TOOL_IMG_HEIGHT*1.2)))
HERRAMIENTAS_IMGS["Pegamento"] = load_image("Pegamento.png", (TOOL_IMG_WIDTH, TOOL_IMG_HEIGHT))
HERRAMIENTAS_IMGS["Lija"]      = load_image("Lija.png",      (TOOL_IMG_WIDTH, TOOL_IMG_HEIGHT))
HERRAMIENTAS_IMGS["Tornillos"] = load_image("Tornillos.png", (TOOL_IMG_WIDTH, TOOL_IMG_HEIGHT))
HERRAMIENTAS_IMGS["Pintura"]   = load_image("Pintura.png",   (TOOL_IMG_WIDTH, TOOL_IMG_HEIGHT))
HERRAMIENTAS_IMGS["Trapo"]     = load_image("Trapo.png",     (TOOL_IMG_WIDTH, TOOL_IMG_HEIGHT))
HERRAMIENTAS_IMGS["Clavos"]    = load_image("Clavos.png",    (TOOL_IMG_WIDTH, TOOL_IMG_HEIGHT))

# ================== DEFINICIÓN DE ETAPAS ==================
HERRAMIENTAS_NOMBRES = ["Martillo", "Pegamento", "Lija", "Tornillos", "Pintura", "Trapo", "Clavos", "Liga"]

OBJETOS = [
    "Osito de Peluche Roto",
    "Silla Rota",
    "Figura de Madera Rota"
]

REPARACION_ETAPAS = [
    ["Pegamento"],
    ["Tornillos", "Martillo"],
    ["Pegamento", "Liga", "Pintura"]
]

OBJETO_IMAGENES = {
    "Osito de Peluche Roto": {"roto": "oso_R.png", "reparado": "oso_N.png"},
    "Silla Rota": {"roto": "silla_R.png", "reparado": "silla_N.png"},
    "Figura de Madera Rota": {"roto": "figura_maderaR.png", "reparado": "figura_madera.png"}
}

OBJETOS_IMGS_LOADED = {}

# ================== CLASE HERRAMIENTA ==================
class Herramienta(pygame.sprite.Sprite):
    def __init__(self, x, y, ancho, alto, nombre):
        super().__init__()
        self.nombre = nombre
        self.seleccionada = False
        self.image = pygame.Surface([ancho, alto], pygame.SRCALPHA)

        # Fondo de tarjeta redondeado
        rect = self.image.get_rect()
        draw_rounded_rect(self.image, COLOR_FONDO_HERRAMIENTA, rect, radius=22)
        draw_rounded_rect(self.image, COLOR_BORDE_HERRAMIENTA, rect, radius=22, width=3)

        # Icono de herramienta
        tool_img = HERRAMIENTAS_IMGS.get(nombre)
        if tool_img:
            img_x = (ancho - tool_img.get_width()) // 2
            img_y = (alto - tool_img.get_height()) // 2 - 8
            self.image.blit(tool_img, (img_x, img_y))
        else:
            temp_surface = pygame.Surface([TOOL_IMG_WIDTH, TOOL_IMG_HEIGHT], pygame.SRCALPHA)
            temp_surface.fill(AZUL_HERRAMIENTA)
            img_x = (ancho - TOOL_IMG_WIDTH) // 2
            img_y = (alto - TOOL_IMG_HEIGHT) // 2 - 8
            self.image.blit(temp_surface, (img_x, img_y))

        self.rect = self.image.get_rect(topleft=(x, y))

# ================== FONDO ==================
FONDO_NIVEL2 = load_image("pibble_fondo.png", (ANCHO, ALTO), convert_alpha=False, fallback_color=(30,144,255,255))

# ================== CLASE ENEMIGO DISTRACTOR ==================
class EnemigoDistractor:
    """Enemigo que aparece brevemente para distraer al jugador."""
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.activo = False
        self.tiempo_aparicion = 0.0
        self.duracion_aparicion = 2.0  # Duración en segundos
        self.velocidad_animacion = 0.0
        self.alpha = 0
        self.scale = 0.5
        self.x = 0
        self.y = 0
        self.invertir_controles = False  # Flag para invertir controles en modo difícil
        
        # Cargar imagen del enemigo (gato malvado)
        try:
            self.imagen_original = load_image("bat_cat.png", (200, 200), convert_alpha=True)
        except:
            # Si no se puede cargar, crear una imagen de fallback
            self.imagen_original = pygame.Surface((200, 200), pygame.SRCALPHA)
            pygame.draw.circle(self.imagen_original, (255, 0, 0), (100, 100), 80)
            pygame.draw.circle(self.imagen_original, (0, 0, 0), (80, 80), 15)
            pygame.draw.circle(self.imagen_original, (0, 0, 0), (120, 80), 15)
        
        self.imagen = self.imagen_original.copy()
        self.rect = self.imagen.get_rect()
        
        # Mensajes distractores
        self.mensajes = [
            "¡JAJAJA!",
            "¡NO PODRÁS!",
            "¡MUAHAHA!",
            "¡TE DISTRAIGO!",
            "¡MIRA AQUÍ!",
            "¡JA JA JA!"
        ]
        self.mensajes_profesional = [
            "¡CONTROLES INVERTIDOS!",
            "¡JAJAJA!",
            "¡AHORA ES PRO!",
            "¡MUAHAHA!",
            "¡TE CONFUNDO!",
            "¡JA JA JA!"
        ]
        self.mensaje_actual = ""
        self.font_mensaje = pygame.font.Font(None, 72)
    
    def activar(self):
        """Activa el enemigo en una posición aleatoria."""
        if not self.activo:
            self.activo = True
            self.tiempo_aparicion = 0.0
            self.velocidad_animacion = 0.0
            self.alpha = 0
            self.scale = 0.5
            
            # Posición aleatoria (evitar el centro donde está el objeto)
            self.x = random.randint(100, self.screen_width - 300)
            self.y = random.randint(100, self.screen_height - 300)
            
            # Mensaje aleatorio (diferente si invierte controles)
            if self.invertir_controles:
                self.mensaje_actual = random.choice(self.mensajes_profesional)
            else:
                self.mensaje_actual = random.choice(self.mensajes)
            
            self.rect.center = (self.x, self.y)
    
    def update(self, delta_time):
        """Actualiza la animación del enemigo."""
        if self.activo:
            self.tiempo_aparicion += delta_time
            self.velocidad_animacion += delta_time * 8.0  # Velocidad de animación
            
            # Animación de entrada (primeros 0.5 segundos)
            if self.tiempo_aparicion < 0.5:
                progress = self.tiempo_aparicion / 0.5
                self.scale = 0.5 + (1.0 - 0.5) * progress
                self.alpha = int(255 * progress)
            # Animación de salida (últimos 0.5 segundos)
            elif self.tiempo_aparicion > self.duracion_aparicion - 0.5:
                progress = (self.tiempo_aparicion - (self.duracion_aparicion - 0.5)) / 0.5
                self.scale = 1.0 - (0.3 * progress)
                self.alpha = int(255 * (1.0 - progress))
            else:
                # En el medio, mantener tamaño y opacidad
                self.scale = 1.0
                self.alpha = 255
                # Efecto de "respiración" sutil
                self.scale = 1.0 + 0.1 * math.sin(self.velocidad_animacion)
            
            # Actualizar imagen escalada
            new_size = (int(200 * self.scale), int(200 * self.scale))
            self.imagen = pygame.transform.scale(self.imagen_original, new_size)
            self.imagen.set_alpha(self.alpha)
            self.rect = self.imagen.get_rect(center=(self.x, self.y))
            
            # Desactivar después del tiempo
            if self.tiempo_aparicion >= self.duracion_aparicion:
                self.activo = False
    
    def draw(self, screen):
        """Dibuja el enemigo en la pantalla."""
        if self.activo and self.alpha > 0:
            screen.blit(self.imagen, self.rect)
            
            if self.alpha > 100:
                mensaje_surf = self.font_mensaje.render(self.mensaje_actual, True, (255, 255, 0))
                mensaje_surf.set_alpha(self.alpha)
                mensaje_rect = mensaje_surf.get_rect(center=(self.x, self.y - 150))
                
                fondo_mensaje = pygame.Surface((mensaje_rect.width + 20, mensaje_rect.height + 10), pygame.SRCALPHA)
                fondo_mensaje.fill((0, 0, 0, min(200, self.alpha)))
                screen.blit(fondo_mensaje, (mensaje_rect.x - 10, mensaje_rect.y - 5))
                screen.blit(mensaje_surf, mensaje_rect)
            
            if self.alpha > 150:
                glow_surface = pygame.Surface((self.rect.width + 40, self.rect.height + 40), pygame.SRCALPHA)
                glow_alpha = int((self.alpha - 150) * 0.3)
                pygame.draw.circle(
                    glow_surface,
                    (255, 0, 0, glow_alpha),
                    (glow_surface.get_width() // 2, glow_surface.get_height() // 2),
                    min(glow_surface.get_width(), glow_surface.get_height()) // 2
                )
                screen.blit(glow_surface, (self.rect.x - 20, self.rect.y - 20))

# ================== NIVEL 2 ==================
def run_level2(dificultad, idioma, screen):
    global ANCHO, ALTO, fuente, clock, FPS, FONDO_NIVEL2, OBJETO_IMAGENES, OBJETOS_IMGS_LOADED

    if not OBJETOS_IMGS_LOADED:
        OBJETO_DISPLAY_SIZE = (300, 300)
        for obj_name, paths in OBJETO_IMAGENES.items():
            OBJETOS_IMGS_LOADED[obj_name] = {}
            for state, filename in paths.items():
                color = ROJO_ROTO if state == "roto" else VERDE_REPARACION
                OBJETOS_IMGS_LOADED[obj_name][state] = load_image(
                    filename, OBJETO_DISPLAY_SIZE, fallback_color=(*color, 200)
                )

    # Mostrar tutorial del nivel 2 antes de empezar, usando el fondo del nivel (opaco)
    try:
        tut_res = mostrar_tutorial_nivel2(screen, FONDO_NIVEL2)
        if tut_res == "salir_juego":
            return "salir_juego"
    except Exception as e:
        # Si falla el tutorial, continuar sin bloquear el nivel
        print(f"Advertencia: fallo al mostrar tutorial nivel 2: {e}")

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
    
    enemigo = EnemigoDistractor(ANCHO, ALTO)
    enemigo_timer = 0.0
    es_modo_profesional = dificultad.lower() in ["profesional"]

    if dificultad.lower() in ["principiante"]:
        enemigo_intervalo_min = 8.0
        enemigo_intervalo_max = 12.0
    elif es_modo_profesional:
        enemigo_intervalo_min = 4.0
        enemigo_intervalo_max = 6.0
        enemigo.invertir_controles = True
    else:
        enemigo_intervalo_min = 3.5
        enemigo_intervalo_max = 5.5
    
    proxima_aparicion = random.uniform(enemigo_intervalo_min, enemigo_intervalo_max)

    tool_ancho = TOOL_DISPLAY_WIDTH
    tool_alto = TOOL_DISPLAY_HEIGHT
    gap = 20
    herramientas_list = []

    num_herramientas = len(HERRAMIENTAS_NOMBRES)
    num_columnas = 2
    num_filas = num_herramientas // num_columnas

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
            enemigo.update(delta_time)
            
            if not enemigo.activo:
                enemigo_timer += delta_time
                if enemigo_timer >= proxima_aparicion:
                    enemigo.activar()
                    enemigo_timer = 0.0
                    proxima_aparicion = random.uniform(enemigo_intervalo_min, enemigo_intervalo_max)
            
            if success_flash_timer > 0:
                success_flash_timer -= delta_time
                if success_flash_timer < 0:
                    success_flash_timer = 0.0

            if objeto_reparado_timer == 0.0:
                tiempo_restante -= delta_time

            if tiempo_restante <= 0:
                tiempo_restante = 0
                juego_finalizado = True
                mensaje_feedback = get_text("¡TIEMPO AGOTADO!", idioma)

            if mensaje_timer > 0:
                mensaje_timer -= delta_time
                if mensaje_timer <= 0:
                    mensaje_feedback = ""

            if objeto_reparado_timer > 0:
                objeto_reparado_timer -= delta_time
                if objeto_reparado_timer <= 0:
                    objeto_reparado_timer = 0.0
                    objeto_actual_index += 1
                    etapa_actual = 0
                    if objeto_actual_index >= len(OBJETOS):
                        juego_finalizado = True
                        mensaje_feedback = get_text("¡NIVEL COMPLETADO!", idioma)
                        mensaje_timer = 3.0
                    else:
                        objeto_nombre = OBJETOS[objeto_actual_index]
                        objeto_nombre_traducido = get_text(objeto_nombre, idioma) if objeto_nombre in ["Osito de Peluche Roto", "Silla Rota", "Figura de Madera Rota"] else objeto_nombre
                        mensaje_feedback = f"{get_text('Continúa con: ', idioma)}{objeto_nombre_traducido}"
                        mensaje_timer = 2.0

            if vidas <= 0 and not juego_finalizado:
                juego_finalizado = True
                mensaje_feedback = get_text("¡SIN VIDAS! JUEGO TERMINADO", idioma)

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    return "salir_juego"

                elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                    accion = mostrar_menu_pausa(screen, ALTO, ANCHO, idioma)
                    if accion == "reiniciar":
                        return "reiniciar"
                    elif accion == "salir":
                        return "salir_menu"

                elif evento.type == pygame.KEYDOWN and not juego_finalizado and objeto_reparado_timer == 0.0:
                    herramientas_list[index_seleccionado].seleccionada = False

                    controles_invertidos = es_modo_profesional and enemigo.activo and enemigo.invertir_controles
                    
                    if controles_invertidos:
                        tecla_arriba = (pygame.K_s, pygame.K_DOWN)
                        tecla_abajo = (pygame.K_w, pygame.K_UP)
                        tecla_derecha = (pygame.K_a, pygame.K_LEFT)
                        tecla_izquierda = (pygame.K_d, pygame.K_RIGHT)
                    else:
                        tecla_arriba = (pygame.K_w, pygame.K_UP)
                        tecla_abajo = (pygame.K_s, pygame.K_DOWN)
                        tecla_derecha = (pygame.K_d, pygame.K_RIGHT)
                        tecla_izquierda = (pygame.K_a, pygame.K_LEFT)

                    if evento.key in tecla_abajo:
                        if index_seleccionado + 2 < len(herramientas_list):
                            index_seleccionado = index_seleccionado + 2
                        else:
                            index_seleccionado = (index_seleccionado + 1) % len(herramientas_list)
                    elif evento.key in tecla_arriba:
                        if index_seleccionado - 2 >= 0:
                            index_seleccionado = index_seleccionado - 2
                        else:
                            index_seleccionado = (index_seleccionado - 1) % len(herramientas_list)
                    elif evento.key in tecla_derecha:
                        if index_seleccionado % 2 == 0:
                            index_seleccionado = (index_seleccionado + 1) % len(herramientas_list)
                    elif evento.key in tecla_izquierda:
                        if index_seleccionado % 2 != 0:
                            index_seleccionado = (index_seleccionado - 1) % len(herramientas_list)

                    index_seleccionado = index_seleccionado % len(herramientas_list)
                    herramientas_list[index_seleccionado].seleccionada = True

                    if evento.key == pygame.K_RETURN:
                        herramienta_usada = herramientas_list[index_seleccionado].nombre
                        if objeto_actual_index < len(OBJETOS):
                            herramientas_necesarias = REPARACION_ETAPAS[objeto_actual_index]
                            if etapa_actual >= len(herramientas_necesarias):
                                continue
                            herramienta_correcta_actual = herramientas_necesarias[etapa_actual]

                            if herramienta_usada == herramienta_correcta_actual:
                                etapa_actual += 1
                                success_flash_timer = 0.5
                                if etapa_actual >= len(herramientas_necesarias):
                                    objeto_reparado_timer = 4.0
                                    mensaje_feedback = get_text("¡OBJETO REPARADO! Esperando 4 segundos...", idioma)
                                    mensaje_timer = 4.0
                                else:
                                    siguiente_tool = herramientas_necesarias[etapa_actual]
                                    mensaje_feedback = get_text("¡Herramienta '", idioma) + herramienta_usada + get_text("' CORRECTA! Siguiente: ", idioma) + siguiente_tool
                                    mensaje_timer = 2.0
                            else:
                                vidas -= 1
                                mensaje_feedback = f"{get_text('HERRAMIENTA INCORRECTA: Se resta 1 vida. (Vidas restantes: ', idioma)}{vidas})"
                                mensaje_timer = 2.0

        # ================== DIBUJO ==================
        if FONDO_NIVEL2:
            screen.blit(FONDO_NIVEL2, (0, 0))
        else:
            screen.fill(AZUL_FONDO)

        area_trabajo_surface = pygame.Surface((ANCHO // 2, int(ALTO * 0.75)), pygame.SRCALPHA)
        area_trabajo_surface.fill((255, 255, 255, 200))
        area_trabajo_rect = area_trabajo_surface.get_rect(topleft=(ANCHO // 4, ALTO // 8))
        draw_rounded_rect(area_trabajo_surface, (255, 255, 255, 255), area_trabajo_surface.get_rect(), radius=30, width=4)
        screen.blit(area_trabajo_surface, area_trabajo_rect.topleft)

        objeto_display_size = (300, 300)
        objeto_roto_rect = pygame.Rect(
            area_trabajo_rect.centerx - objeto_display_size[0] // 2,
            area_trabajo_rect.centery - objeto_display_size[1] // 2,
            objeto_display_size[0],
            objeto_display_size[1]
        )

        # PANEL VIDAS (sin icono)
        vidas_texto = f"{get_text('Vidas', idioma)}: {vidas}"
        vidas_surf, _ = render_text_shrink(vidas_texto, max_width=220, color=BLANCO, base_size=36)
        vidas_rect = vidas_surf.get_rect()
        vidas_box = pygame.Rect(40, 20, vidas_rect.width + 30, vidas_rect.height + 16)
        draw_rounded_rect(screen, ROJO_VIDA, vidas_box, radius=18)
        draw_rounded_rect(screen, BLANCO, vidas_box, radius=18, width=2)
        vidas_rect.center = vidas_box.center
        screen.blit(vidas_surf, vidas_rect)

        # BARRA DE TIEMPO + BURBUJA ARRIBA
        BARRA_TIEMPO_ANCHO = ANCHO // 3
        BARRA_TIEMPO_ALTO = 24
        x_barra_tiempo = ANCHO // 2 - BARRA_TIEMPO_ANCHO // 2
        y_barra_tiempo = 60

        pygame.draw.rect(screen, BLANCO, (x_barra_tiempo - 4, y_barra_tiempo - 4,
                                          BARRA_TIEMPO_ANCHO + 8, BARRA_TIEMPO_ALTO + 8), border_radius=15)
        pygame.draw.rect(screen, (200, 200, 200),
                         (x_barra_tiempo, y_barra_tiempo, BARRA_TIEMPO_ANCHO, BARRA_TIEMPO_ALTO),
                         border_radius=12)
        progreso_ancho = int((tiempo_restante / tiempo_total) * BARRA_TIEMPO_ANCHO)
        pygame.draw.rect(screen, NARANJA_TIEMPO,
                         (x_barra_tiempo, y_barra_tiempo, progreso_ancho, BARRA_TIEMPO_ALTO),
                         border_radius=12)

        texto_tiempo = pygame.font.Font(None, 34).render(
            f"{get_text('Tiempo', idioma)}: {int(tiempo_restante)}s", True, AMARILLO_TIEMPO_TEXTO
        )
        bubble_rect = pygame.Rect(0, 0, texto_tiempo.get_width() + 30, texto_tiempo.get_height() + 16)
        bubble_rect.center = (ANCHO // 2, 25)
        draw_rounded_rect(screen, (148, 0, 211), bubble_rect, radius=20)
        draw_rounded_rect(screen, BLANCO, bubble_rect, radius=20, width=3)
        texto_tiempo_rect = texto_tiempo.get_rect(center=bubble_rect.center)
        screen.blit(texto_tiempo, texto_tiempo_rect)

        objeto_actual_nombre = OBJETOS[objeto_actual_index] if objeto_actual_index < len(OBJETOS) else get_text("¡TERMINADO!", idioma)
        objeto_nombre_traducido = get_text(objeto_actual_nombre, idioma) if objeto_actual_nombre in ["Osito de Peluche Roto", "Silla Rota", "Figura de Madera Rota"] else objeto_actual_nombre
        objeto_texto = f"{get_text('OBJETO', idioma)}: {objeto_nombre_traducido}"
        objeto_surf, _ = render_text_shrink(objeto_texto, max_width=area_trabajo_rect.width - 40,
                                            color=AZUL_HERRAMIENTA, base_size=40)
        objeto_rect = objeto_surf.get_rect()
        objeto_rect.center = (area_trabajo_rect.centerx, area_trabajo_rect.top + 40)
        screen.blit(objeto_surf, objeto_rect)

        CAJA_PISTA_ANCHO = 260
        CAJA_PISTA_ALTO = 170
        x_pista = 50
        y_pista = ALTO // 2 - CAJA_PISTA_ALTO // 2
        pista_rect = pygame.Rect(x_pista, y_pista, CAJA_PISTA_ANCHO, CAJA_PISTA_ALTO)

        draw_rounded_rect(screen, (255, 255, 200), pista_rect, radius=25)
        draw_rounded_rect(screen, (255, 215, 0), pista_rect, radius=25, width=3)

        pista_titulo_texto = get_text("HERRAMIENTA REQUERIDA", idioma)
        pista_titulo_surf, _ = render_text_shrink(pista_titulo_texto, max_width=CAJA_PISTA_ANCHO - 20,
                                                  color=AZUL_HERRAMIENTA, base_size=30)
        pista_titulo_rect = pista_titulo_surf.get_rect()
        pista_titulo_rect.center = (pista_rect.centerx, pista_rect.top + 25)
        screen.blit(pista_titulo_surf, pista_titulo_rect)

        if not juego_finalizado and objeto_actual_index < len(OBJETOS) and objeto_reparado_timer == 0.0:
            herramientas_necesarias = REPARACION_ETAPAS[objeto_actual_index]
            pista_tool_nombre = herramientas_necesarias[etapa_actual]
            pista_tool_img = HERRAMIENTAS_IMGS.get(pista_tool_nombre)
            if pista_tool_img:
                scaled_img = pygame.transform.scale(pista_tool_img, (80, 80))
                img_pista_x = pista_rect.centerx - scaled_img.get_width() // 2
                img_pista_y = pista_rect.top + 60
                screen.blit(scaled_img, (img_pista_x, img_pista_y))
            else:
                pista_contenido_surf, _ = render_text_shrink(
                    pista_tool_nombre, max_width=CAJA_PISTA_ANCHO - 20,
                    color=ROJO_ROTO, base_size=32
                )
                pista_contenido_rect = pista_contenido_surf.get_rect()
                pista_contenido_rect.center = (pista_rect.centerx, pista_rect.top + 80)
                screen.blit(pista_contenido_surf, pista_contenido_rect)
        elif objeto_reparado_timer > 0.0:
            pista_contenido_surf, _ = render_text_shrink(
                get_text("REPARADO", idioma), max_width=CAJA_PISTA_ANCHO - 20,
                color=VERDE_REPARACION, base_size=36
            )
            pista_contenido_rect = pista_contenido_surf.get_rect()
            pista_contenido_rect.center = (pista_rect.centerx, pista_rect.centery)
            screen.blit(pista_contenido_surf, pista_contenido_rect)
        else:
            pista_contenido_surf, _ = render_text_shrink(
                get_text("FIN DEL JUEGO", idioma), max_width=CAJA_PISTA_ANCHO - 20,
                color=ROJO_ROTO, base_size=30
            )
            pista_contenido_rect = pista_contenido_surf.get_rect()
            pista_contenido_rect.center = (pista_rect.centerx, pista_rect.centery)
            screen.blit(pista_contenido_surf, pista_contenido_rect)

        for herramienta in herramientas_list:
            if herramienta.seleccionada and objeto_reparado_timer == 0.0:
                sel_rect = herramienta.rect.inflate(12, 12)
                draw_rounded_rect(screen, AMARILLO_SELECCION, sel_rect, radius=26, width=5)

            screen.blit(herramienta.image, herramienta.rect)

            nombre_max_width = herramienta.rect.width - 16
            nombre_surf, _ = render_text_shrink(
                herramienta.nombre, max_width=nombre_max_width,
                color=BLANCO, base_size=26
            )
            nombre_rect = nombre_surf.get_rect()
            nombre_rect.centerx = herramienta.rect.centerx
            nombre_rect.bottom = herramienta.rect.bottom - 4
            screen.blit(nombre_surf, nombre_rect)

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

        if success_flash_timer > 0.0:
            flash_surface = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            flash_surface.fill(VERDE_TRANSPARENTE)
            screen.blit(flash_surface, (0, 0))
        
        enemigo.draw(screen)

        # MENSAJE INFERIOR
        modo_tutorial = False

        if objeto_reparado_timer > 0.0:
            estado_texto = f"{get_text('OBJETO REPARADO! Siguiente objeto en', idioma)} {int(objeto_reparado_timer) + 1} {get_text('segundos...', idioma)}"
            color_estado = VERDE_REPARACION
        elif mensaje_feedback:
            estado_texto = mensaje_feedback
            color_estado = ROJO_ROTO if ("INCORRECTA" in mensaje_feedback or "AGOTADO" in mensaje_feedback or "SIN VIDAS" in mensaje_feedback) \
                           else VERDE_REPARACION
        elif juego_finalizado:
            estado_texto = mensaje_feedback
            color_estado = ROJO_ROTO if vidas <= 0 or tiempo_restante <= 0 else VERDE_REPARACION
        else:
            modo_tutorial = True

        if not modo_tutorial:
            estado_surf, _ = render_text_shrink(
                estado_texto, max_width=ANCHO - 200, color=color_estado, base_size=32
            )
            estado_rect = estado_surf.get_rect()
            estado_rect.center = (ANCHO // 2, ALTO - 40)
            screen.blit(estado_surf, estado_rect)
        else:
            banner_width = min(ANCHO - 100, 900)
            banner_rect = pygame.Rect(0, 0, banner_width, 70)
            banner_rect.center = (ANCHO // 2, ALTO - 45)

            # Fondo rosa neón y borde amarillo
            draw_rounded_rect(screen, (255, 20, 147), banner_rect, radius=25)
            draw_rounded_rect(screen, (255, 255, 0), banner_rect, radius=25, width=4)

            font_banner = pygame.font.Font(None, 36)

            text1 = font_banner.render("Presiona ", True, BLANCO)
            text2 = font_banner.render("ENTER", True, (255, 255, 0))
            text3 = font_banner.render(" para usar la herramienta seleccionada", True, BLANCO)

            total_width = text1.get_width() + text2.get_width() + text3.get_width()
            start_x = banner_rect.centerx - total_width // 2
            y = banner_rect.centery - text1.get_height() // 2

            screen.blit(text1, (start_x, y))
            screen.blit(text2, (start_x + text1.get_width(), y))
            screen.blit(text3, (start_x + text1.get_width() + text2.get_width(), y))

        pygame.display.flip()

        if juego_finalizado:
            victoria = objeto_actual_index >= len(OBJETOS)
            
            if victoria:
                accion = mostrar_menu_victoria(screen, "level2")
                if accion == "siguiente":
                    return "siguiente"
                elif accion == "reintentar":
                    return "reiniciar"
                elif accion == "salir":
                    return "salir_menu"
            else:
                accion = mostrar_menu_derrota(screen)
                if accion == "reintentar":
                    return "reiniciar"
                elif accion == "salir":
                    return "salir_menu"

    return "siguiente"

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((ANCHO, ALTO))
    accion = "iniciar"
    while accion != "salir_juego":
        if accion in ("iniciar", "reiniciar"):
            accion = run_level2(dificultad="Intermedio", idioma="Español", screen=screen)
        elif accion == "salir_menu":
            accion = "salir_juego"
    pygame.quit()
    sys.exit()