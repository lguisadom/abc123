# 🤖 Simulación Robots Monstruicidas vs Monstruos

## 📋 Descripción del Proyecto

Este proyecto implementa una simulación 3D completa de robots monstruicidas que cazan monstruos en un entorno energético tridimensional, desarrollado para el examen parcial del curso "Fundamentos de Inteligencia Artificial - MIA-103".

## 🏗️ Estructura del Proyecto

```
examen-parcial/
├── main.py                    # Script principal de simulación
├── config.py                  # Configuración centralizada
├── environment.py             # Clase Environment 3D
├── robot.py                   # Clase Robot con sensores y memoria
├── monster.py                 # Clase Monster (agente reflejo simple)
├── rule_engine.py             # Motor de reglas CSV
├── requirements.txt           # Dependencias de Python
├── README.md                  # Este archivo
├── data/                      # Datos del proyecto
│   ├── robot_rules.csv        # Reglas de percepción-acción del robot
│   └── monster_rules.csv      # Reglas de percepción-acción del monstruo
├── docs/                      # Documentación técnica
│   ├── README.md              # Índice de documentación
│   ├── PHASES_TRACKING.md     # Seguimiento de fases
│   ├── CONFIGURATION_GUIDE.md # Guía de configuración
│   ├── RULES_SYSTEM.md        # Sistema de reglas
│   └── ...                    # Otros documentos técnicos
└── instruccions/              # Instrucciones del examen
    ├── 1 enunciado.md
    ├── 2 tabla percepcion-accion del robot.png
    ├── 3 tabla percepcion-accion del monstruo.png
    └── 4 nomenclaturas usadas para entender las tablas.png
```

## ✅ **Estado del Proyecto: COMPLETADO**

### 🎯 **Fases Implementadas**

- ✅ **Fase 1**: Estructura básica del proyecto y entorno 3D
- ✅ **Fase 2**: Implementar entidades básicas (Robot y Monstruo)
- ✅ **Fase 3**: Sistema de carga de reglas desde CSV
- ✅ **Fase 4**: Implementar sensores completos del robot
- ✅ **Fase 4.5**: Corrección del monstruo según especificaciones
- ✅ **Fase 4.6**: Centralización de variables globales
- ✅ **Fase 4.7**: Reorganización de config.py

### 🚀 **Características Implementadas**

#### 🌍 **Entorno 3D**
- Mundo N×N×N configurable
- Zonas libres (verde) y vacías (rojo transparente)
- Fronteras invisibles
- Visualización con Plotly usando Mesh3d

#### 🤖 **Robots Monstruicidas**
- Sensores completos: Giroscopio, Monstroscopio, Vacuscopio, Energómetro, Roboscanner
- Memoria interna con límite configurable
- Comportamiento basado en reglas CSV
- Comunicación robot-robot
- Destrucción de monstruos (mutual sacrifice)

#### 👹 **Monstruos**
- Agente reflejo simple (sin orientación propia)
- Sistema de coordenadas global absoluto
- Comportamiento 100% basado en CSV
- Parámetros K (frecuencia) y p (probabilidad)
- Acciones probabilísticas y determinísticas

#### ⚙️ **Sistema de Reglas**
- Motor de reglas CSV para robots y monstruos
- 18 reglas para robots, 64 reglas para monstruos
- Coincidencia exacta de percepciones
- Acciones editables externamente

#### 🎨 **Visualización**
- Cubos 3D reales usando Mesh3d
- Robots como cubos sólidos cyan
- Monstruos con múltiples opciones de visualización
- Bordes grises entre cubos
- Información detallada en leyenda

### 📊 **Configuración Centralizada**

Todas las variables están centralizadas en `config.py`:

```python
# Entorno
WORLD_SIZE = 5
NUM_ROBOTS = 1
NUM_MONSTERS = 2
SIMULATION_STEPS = 100

# Comportamiento
ROBOT_FREQUENCY = 1.0
MONSTER_FREQUENCY = 2.0
MONSTER_PROBABILITY = 0.5

# Visualización
CUBE_SIZE = 3.0
FIGURE_WIDTH = 1500
FIGURE_HEIGHT = 1200
```

### 🧪 **Pruebas y Verificación**

El sistema ha sido probado exhaustivamente:
- ✅ Percepción correcta de sensores
- ✅ Coincidencia de reglas CSV
- ✅ Movimiento y comportamiento de agentes
- ✅ Visualización 3D funcional
- ✅ Integración completa del sistema

### 📦 **Dependencias**

```
plotly>=5.0.0
pandas>=1.3.0
numpy>=1.21.0
```

### 🚀 **Ejecución**

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar simulación completa
python main.py

# Ver documentación
ls docs/
```

### 📚 **Documentación**

Toda la documentación técnica está organizada en la carpeta `docs/`:
- **PHASES_TRACKING.md**: Seguimiento detallado del proyecto
- **CONFIGURATION_GUIDE.md**: Guía completa de configuración
- **RULES_SYSTEM.md**: Documentación del sistema de reglas
- **VISUALIZATION_OPTIONS.md**: Opciones de visualización

### 🎯 **Próximas Mejoras**

- **Fase 5**: Sistema de memoria interna del robot (experiencias, aprendizaje)
- **Fase 6**: Visualización interactiva con Plotly (animación, controles)
- **Fase 7**: Optimización para Google Colab (versión de un solo botón)

---

*Desarrollado para el examen parcial de Fundamentos de Inteligencia Artificial - MIA-103*