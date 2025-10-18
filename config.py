# =============================================================================
# CONFIGURACIÓN DE LA SIMULACIÓN - ROBOTS MONSTRUICIDAS VS MONSTRUOS
# =============================================================================
# Este archivo contiene todas las variables de configuración centralizadas
# para facilitar la modificación de parámetros sin tocar el código principal
# =============================================================================

# =============================================================================
# 🌍 CONFIGURACIÓN DEL ENTORNO 3D
# =============================================================================
WORLD_SIZE = 6              # Tamaño del mundo (N×N×N) - Reducido para mejor visualización
PERCENTAGE_FREE = 0.7       # Porcentaje de zonas libres (70%)
PERCENTAGE_EMPTY = 0.3      # Porcentaje de zonas vacías (30%)
INTERNAL_EMPTY_RATIO = 0.3  # Ratio de zonas vacías internas (30% del porcentaje total)

# =============================================================================
# 🤖👹 CONFIGURACIÓN DE ENTIDADES
# =============================================================================
NUM_ROBOTS = 20              # Número de robots en la simulación
NUM_MONSTERS = 20            # Número de monstruos en la simulación

# =============================================================================
# 📍 CONFIGURACIÓN DE POSICIONAMIENTO DE ROBOTS
# =============================================================================
ROBOT_POSITION_MODE = "random"  # "random" o "fixed"
ROBOT_FIXED_POSITION = (2, 2, 2)  # Posición fija si ROBOT_POSITION_MODE = "fixed"
MONSTER_POSITION_MODE = "random"  # "random" o "fixed"
MONSTER_FIXED_POSITION = (1, 1, 1)  # Posición fija si MONSTER_POSITION_MODE = "fixed"

# =============================================================================
# ⚙️ CONFIGURACIÓN DE SIMULACIÓN
# =============================================================================
SIMULATION_STEPS = 1000     # Número de pasos de simulación
ROBOT_FREQUENCY = 1.0       # Frecuencia del robot (1 percepción por segundo)
MONSTER_FREQUENCY = 5       # Frecuencia del monstruo (cada K segundos)
MONSTER_PROBABILITY = 0.5   # Probabilidad de que el monstruo se mueva en cada turno (parámetro p)

# =============================================================================
# 🎬 CONFIGURACIÓN DE SIMULACIÓN EN TIEMPO REAL
# =============================================================================
REAL_TIME_DELAY = 1.0       # Segundos de pausa entre pasos en tiempo real
REAL_TIME_ENABLED = True    # Habilitar simulación en tiempo real por defecto

# =============================================================================
# 🧠 CONFIGURACIÓN DE MEMORIA Y APRENDIZAJE
# =============================================================================
ROBOT_MEMORY_LIMIT = 1000   # Límite de experiencias en memoria del robot

# =============================================================================
# 🎨 CONFIGURACIÓN DE VISUALIZACIÓN 3D
# =============================================================================
# Dimensiones del lienzo
FIGURE_WIDTH = 1500         # Ancho del lienzo de visualización
FIGURE_HEIGHT = 1200        # Alto del lienzo de visualización
ANIMATION_SPEED = 500       # Velocidad de animación

# Configuración de la vista de cámara
UIREVISION = "constant"     # Mantiene la vista de la cámara entre actualizaciones ("constant" o None)

# Tamaños de elementos visuales
CUBE_SIZE = 3.0             # Tamaño de cada cubo en la visualización
MONSTER_SIZE_PERCENTAGE = 0.7  # Porcentaje del tamaño del cubo que ocupa el monstruo (0.0 = punto, 1.0 = ocupa todo el cubo)

# =============================================================================
# 🎭 CONFIGURACIÓN DE OPACIDAD Y TRANSPARENCIA
# =============================================================================
FREE_ZONE_OPACITY = 0.7        # Opacidad de las zonas libres
MONSTER_OPACITY = 0.7          # Opacidad de los monstruos
MONSTER_SHADOW_OPACITY = 0.5   # Opacidad de sombras de monstruos
BORDER_OPACITY = 0.2           # Opacidad de bordes

# =============================================================================
# 📍 CONFIGURACIÓN DE POSICIONAMIENTO VISUAL
# =============================================================================
MONSTER_CENTER_OFFSET = 0.5    # Offset para centrar monstruos en cubos

# =============================================================================
# 👹 CONFIGURACIÓN DE VISUALIZACIÓN DE MONSTRUOS
# =============================================================================
MONSTER_VISUALIZATION = "void"  # Opciones: "cloud", "mist", "energy", "void", "shadow"

# =============================================================================
# 🎨 CONFIGURACIÓN DE COLORES
# =============================================================================
# Colores para robots
ROBOT_COLOR = "cyan"                    # Color principal del robot
ROBOT_ARROW_COLOR = "red"               # Color de la flecha de orientación del robot

# Colores para monstruos (según tipo de visualización)
MONSTER_COLOR_CLOUD = "red"             # Color para monstruos tipo "cloud"
MONSTER_COLOR_MIST = "purple"           # Color para monstruos tipo "mist"
MONSTER_COLOR_ENERGY = "yellow"         # Color para monstruos tipo "energy"
MONSTER_COLOR_VOID = "red"            # Color para monstruos tipo "void"
MONSTER_COLOR_SHADOW = "gray"           # Color para monstruos tipo "shadow"

# Colores para zonas del entorno
FREE_ZONE_COLOR = "lightgreen"          # Color de las zonas libres
EMPTY_ZONE_COLOR = "black"                # Color de las zonas vacías internas
CUBE_BORDER_COLOR = "gray"              # Color de los bordes de los cubos

# =============================================================================
# 📝 NOTAS DE CONFIGURACIÓN
# =============================================================================# 
# Para cambiar la configuración:
# 1. Modifica las variables en este archivo
# 2. Reinicia la simulación para aplicar los cambios
# 3. Consulta CONFIGURATION_GUIDE.md para más detalles
# =============================================================================