# ♻️ EcoGuardianes: Misión ODS 12

![Idiomas](https://img.shields.io/badge/idiomas-ES%20%7C%20EN-orange.svg)
![Licencia](https://img.shields.io/badge/licencia-MIT-blue.svg)
![Versión](https://img.shields.io/badge/version-1.0.0-green.svg)

Un videojuego educativo 2D diseñado para niños y niñas de **6 a 12 años**. El proyecto se centra en enseñar los principios del **Objetivo de Desarrollo Sostenible (ODS) 12: Producción y Consumo Responsables**, utilizando como base las **7R** (Rediseñar, Reducir, Reutilizar, Reparar, Renovar, Recuperar y Reciclar.).
El objetivo es concienciar sobre la gestión de residuos y el consumo responsable de una manera divertida, interactiva y, sobre todo, adaptada a sus edades.

![Imagen de WhatsApp 2025-11-12 a las 07 43 35_fe79cd7c](https://github.com/user-attachments/assets/f83fde9f-4c65-48b6-8795-67a5878ecc8a)

---

## ✨ Características Principales

* **Público Adaptativo:** El juego incluye **3 etapas de dificultad** (Principiante, Intermedio, Avanzado). Esta configuración ajusta la velocidad y complejidad de los minijuegos para adaptarse al rango de edad de 6 a 12 años.
* **Menú de Opciones:** Un menú de configuración completo que permite al jugador:
    * Ajustar el **Volumen** (Música y Efectos de Sonido).
    * Seleccionar la **Dificultad**.
    * Cambiar el **Idioma** (Inglés y Español).

---

## 🕹️ Los Niveles del Juego

El juego se compone de tres minijuegos principales, cada uno enfocado en una "R" diferente.

### Nivel 1: ¡El Río Contaminado! (Reducir / Reciclar)

En este nivel, el jugador debe limpiar un río clasificando la basura que cae.

* **Mecánica:** Hay 3 botes de basura en la parte inferior de la pantalla. La basura cae desde un río en la parte superior.
* **Objetivo:** El jugador debe recolectar la basura que cae en el bote correcto.
* **Reglas:**
    * Cada basura errada (colocada en el bote incorrecto) resta puntos.
    * **¡Giro clave!** Cuando un bote de basura se completa (alcanza su meta), se bloquea, deja de moverse y ya no suma más puntos. Esto incrementa el desafío al forzar al jugador a gestionar los contenedores restantes.
* **Esenario para la etapa 1:**

![Texto alternativo](img/rio.png)

### Nivel 2: El Taller de Reparaciones (Reparar / Renovar / Recuperar))

Este nivel se enfoca en la importancia de reparar objetos en lugar de desecharlos.

* **Mecánica:** Aparece un objeto roto en el centro de la pantalla.
* **Objetivo:** A un lado, el jugador tiene un panel con las herramientas necesarias (martillo, destornillador, pegamento, etc.). Debe seleccionar la herramienta correcta y aplicarla en la zona dañada.
* **Desafío:** Un **"enemigo distractor"** aparecerá en pantalla para interrumpir al jugador y evitar que complete su tarea a tiempo (ej. tapando la visión, moviendo las herramientas).

### Nivel 3: La Cinta Transformadora (Reutilizar / Rediseñar)

El nivel final enseña cómo los objetos "viejos" pueden tener una nueva vida y propósito.

* **Mecánica:** Es un nivel de ritmo (Quick Time Event - QTE). Una cinta transportadora mueve diferentes objetos (llantas, botellas, cajas).
* **Objetivo:** Los objetos pasan por un lugar determinado ("zona de transformación").
* **Acción:** Justo en ese momento, una tecla aleatoria aparece en pantalla. El jugador debe presionar la tecla indicada en el instante preciso para **transformar el objeto** en algo nuevo y útil.

---

## 🧪 Pruebas y Validación del Proyecto

Para asegurar que el juego cumple sus objetivos educativos y es genuinamente divertido, se seguirá un proceso de validación en dos fases:

1.  **Prueba de Campo:** Se realizará una sesión de juego supervisada en una escuela primaria con niños y niñas del rango de edad objetivo (6-12 años).
2.  **Encuesta General:** Inmediatamente después de la prueba de campo, se aplicará una encuesta a los participantes para recolectar retroalimentación cualitativa y cuantitativa.

### Métrica de la Encuesta

La encuesta se centrará en responder las siguientes preguntas:

Jugabilidad 
1. ¿Fue fácil entender cómo se juega? 
☐ Sí  ☐ Más o menos  ☐ No 
2. ¿Los controles (teclas o movimientos) fueron fáciles de usar? 
☐ Sí ☐ No  ☐ A veces  
Diversión 
3. En una escala del 1 al 5, ¿qué tan divertido te pareció el juego? 
� 1 = Nada divertido  � 5 = Muy divertido 
☐ 1 ☐ 2 ☐ 3 ☐ 4 ☐ 5 
4. ¿Qué parte del juego te gustó más? 
☐ Atrapar la basura en el río ☐ Reparar objetos ☐ Transformar la basura en nuevos objetos ☐ Otra (¿cuál?): _____________________________ 
Diseño visual 
5. ¿Te gustaron los colores, dibujos y personajes del juego? 
☐ Sí, mucho ☐ Están bien ☐ No mucho 
6. Si pudieras cambiar algo del diseño, ¿qué sería? (Por ejemplo: colores, personajes, 
fondo, etc.) 
✍
 ️ ______________________________________________________ 
Dificultad 
7. ¿El juego te pareció…? 
☐ Muy fácil ☐ Justo ☐ Muy difícil 
8. ¿Hubo alguna parte que no entendiste o te costó pasar? 
✍
 ️ ______________________________________________________ 
Aprendizaje 
9. Después de jugar, ¿aprendiste algo nuevo sobre cómo cuidar el planeta o las 7R? 
☐ Sí ☐ Un poco ☐ No 
10. Cuéntanos una cosa que aprendiste o recordaste gracias al juego. 
✍
 ️ ______________________________________________________ 
Sugerencias 
11. ¿Qué cambiarías o mejorarías del juego? 
✍
 ️ ______________________________________________________ 
12. ¿Te gustaría jugar más niveles parecidos? 
☐ Sí ☐ Tal vez ☐ No 

---

## 💻 Tecnologías Propuestas

* **Lenguaje de Programación:** Python
* **Diseño de Gráficos:** Libresprite
* **Libreria:** Pygame

## 📄 Licencia

Este proyecto se distribuye bajo la **Licencia MIT**.
