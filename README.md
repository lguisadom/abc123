# 🤖 Simulación Robots Monstruicidas vs Monstruos

## 📋 Descripción del Proyecto

Este proyecto implementa una simulación 3D completa de robots monstruicidas que cazan monstruos en un entorno energético tridimensional. El sistema utiliza un motor de reglas basado en archivos CSV para definir el comportamiento de los agentes, desarrollado para el examen parcial del curso "Fundamentos de Inteligencia Artificial - MIA-103".

## 🏗️ Arquitectura del Sistema

### 🌍 **Entorno 3D (Environment)**

El entorno está implementado como un mundo cúbico de N×N×N celdas donde:
- **Zonas libres (0)**: Espacios donde los agentes pueden moverse
- **Zonas vacías (-1)**: Espacios prohibidos que causan colisiones
- **Bordes**: Fronteras invisibles del mundo

**Características principales**:
- Generación aleatoria de zonas según porcentajes configurables
- Sistema de coordenadas 3D absolutas
- Detección de colisiones y validación de posiciones
- Visualización con cubos 3D usando Plotly Mesh3d

### 🤖 **Robots Monstruicidas**

Los robots son agentes inteligentes con:

#### **Sensores Especializados**:
- **Energómetro**: Detecta monstruos en la celda actual (0=no, 1=sí)
- **Monstroscopio**: Detecta monstruos en 5 direcciones:
  - `Lado1_Top`: Arriba (↑ X+90°)
  - `Lado2_Left`: Izquierda (← Y+90°)
  - `Lado0_Front`: Frente (▲ Z+90°)
  - `Lado3_Right`: Derecha (→ Y-90°)
  - `Lado4_Down`: Abajo (↓ X-90°)
- **Vacuscopio**: Detecta zonas vacías al frente (0=libre, -1=vacía)
- **Roboscanner**: Detecta otros robots al frente (0=no, 2=sí)

#### **Sistema de Orientación 3D**:
- Vector de orientación `[x, y, z]` que indica hacia dónde apunta el robot
- Rotaciones en los tres ejes: X, Y, Z
- Movimiento relativo a la orientación actual

#### **Memoria Interna**:
- Almacena experiencias previas (percepciones + acciones)
- Límite configurable de experiencias
- Consulta memoria antes de aplicar reglas
- **Regla 35 prevalece** sobre memoria cuando detecta zona vacía

#### **Comportamiento**:
- Basado en 35 reglas definidas en `robot_rules.csv`
- Destrucción de monstruos (sacrificio mutuo)
- Comunicación robot-robot en encuentros

### 👹 **Monstruos**

Los monstruos son agentes reflejo simples con:

#### **Características**:
- **Sin orientación propia**: Usan coordenadas globales absolutas
- **Sistema de percepción**: Detecta zonas libres en 6 direcciones (Top, Left, Front, Right, Down, Behind)
- **Parámetros de comportamiento**:
  - `K`: Frecuencia de acción (cada K pasos)
  - `p`: Probabilidad de moverse en cada turno

#### **Comportamiento**:
- Basado en 64 reglas definidas en `monster_rules.csv`
- Movimiento aleatorio entre direcciones disponibles
- Acciones probabilísticas y determinísticas

### ⚙️ **Motor de Reglas (RuleEngine)**

El sistema utiliza un motor de reglas que:

#### **Carga de Reglas**:
- Lee archivos CSV con tablas de percepción-acción
- Valida formato y consistencia de reglas
- Almacena reglas en DataFrames de pandas

#### **Aplicación de Reglas**:
- Coincidencia exacta de percepciones
- Retorna acción correspondiente
- Manejo de reglas no encontradas

#### **Reglas Especiales**:
- **Regla 1**: Destrucción de monstruos
- **Regla 35**: Rotación aleatoria cuando detecta zona vacía
- **Regla 34**: Rotación aleatoria cuando detecta otro robot

## 📊 **Sistema de Configuración**

### **Archivo `config.py`**

Todas las variables están centralizadas para facilitar la modificación:

#### **Entorno 3D**:
```python
WORLD_SIZE = 5              # Tamaño del mundo (N×N×N)
PERCENTAGE_FREE = 0.9       # Porcentaje de zonas libres (90%)
PERCENTAGE_EMPTY = 0.1      # Porcentaje de zonas vacías (10%)
```

#### **Entidades**:
```python
NUM_ROBOTS = 2              # Número de robots
NUM_MONSTERS = 3            # Número de monstruos
ROBOT_FREQUENCY = 1.0       # Frecuencia del robot
MONSTER_FREQUENCY = 10      # Frecuencia del monstruo (K)
MONSTER_PROBABILITY = 0.1   # Probabilidad de movimiento (p)
```

#### **Memoria y Aprendizaje**:
```python
ROBOT_MEMORY_LIMIT = 1000   # Límite de experiencias en memoria
```

#### **Visualización**:
```python
FIGURE_WIDTH = 1500         # Ancho del lienzo
FIGURE_HEIGHT = 1200        # Alto del lienzo
CUBE_SIZE = 3.0             # Tamaño de cubos
MONSTER_VISUALIZATION = "void"  # Tipo de visualización
```

## 🎮 **Modos de Ejecución**

### **1. Simulación Básica (`main.py`)**
- Ejecución secuencial sin interfaz web
- Visualización estática con Plotly
- Logs en consola
- Ideal para pruebas rápidas

### **2. Simulación en Tiempo Real (`realtime_3d.py`)**
- Interfaz web interactiva con Dash
- Control en tiempo real (pausa, paso a paso, reinicio)
- Visualización 3D interactiva
- Logs automáticos en CSV
- Puerto configurable (por defecto 8081)

## 📁 **Estructura de Archivos**

```
examen-parcial/
├── main.py                    # Simulación básica
├── realtime_3d.py             # Simulación en tiempo real (RECOMENDADO)
├── config.py                  # Configuración centralizada
├── environment.py             # Clase Environment 3D
├── robot.py                   # Clase Robot con sensores y memoria
├── monster.py                 # Clase Monster (agente reflejo)
├── rule_engine.py             # Motor de reglas CSV
├── robot_logger.py            # Sistema de logging
├── console_formatter.py       # Formateo de consola
├── requirements.txt           # Dependencias
├── data/                      # Datos del proyecto
│   ├── robot_rules.csv        # 35 reglas de robots
│   └── monster_rules.csv      # 64 reglas de monstruos
├── output/                    # Logs de simulaciones
│   └── simulacion_*/          # Directorios con timestamps
│       ├── R001.csv           # Log del robot 1
│       └── R002.csv           # Log del robot 2
└── instructions/              # Instrucciones del examen
    ├── 1 enunciado.md
    ├── 2 tabla percepcion-accion del robot.png
    ├── 3 tabla percepcion-accion del monstruo.png
    ├── 4 nomenclaturas usadas para entender las tablas.png
    ├── 5 examen-parcial.pdf
    └── 6 robot_instructions.md
```

## 🔄 **Flujo de Ejecución**

### **Ciclo Principal**:
1. **Inicialización**: Carga de reglas, creación de entorno y agentes
2. **Percepción**: Cada agente lee su entorno usando sus sensores
3. **Decisión**: Aplicación de reglas o consulta de memoria
4. **Acción**: Ejecución de movimientos, rotaciones o destrucción
5. **Actualización**: Modificación del entorno y registro de cambios
6. **Logging**: Registro de acciones y estados

### **Flujo del Robot**:
```
perceive() → act() → execute_action() → logging
    ↓           ↓           ↓
  Sensores   Decisión   Ejecución
```

### **Flujo del Monstruo**:
```
perceive() → act() → execute_action()
    ↓           ↓           ↓
  Sensores   Regla CSV   Movimiento
```

## 📊 **Sistema de Logging**

### **Archivos CSV Generados**:
- **Formato**: `output/simulacion_YYYYMMDD_HHMMSS/RXXX.csv`
- **Contenido**: Cada paso del robot con información completa
- **Campos**: Posición, orientación, sensores, regla aplicada, acción, memoria

### **Información Registrada**:
- Estado inicial y final del robot
- Percepciones de todos los sensores
- Número de regla aplicada
- Acción original de la regla
- Acción específica ejecutada
- Uso de memoria vs regla
- Timestamps automáticos

## 🎨 **Sistema de Visualización**

### **Elementos Visuales**:
- **Robots**: Cubos sólidos cyan con flecha de orientación roja
- **Monstruos**: Visualización configurable (cloud, mist, energy, void, shadow)
- **Zonas libres**: Cubos verdes semitransparentes
- **Zonas vacías**: Cubos negros semitransparentes
- **Bordes**: Líneas grises entre cubos

### **Interfaz Web**:
- **Controles**: Play/Pause, Paso a paso, Reinicio, Velocidad
- **Información**: Estado actual, estadísticas, logs
- **Visualización 3D**: Interactiva con zoom, rotación, pan

## 📦 **Dependencias**

```
plotly>=5.0.0      # Visualización 3D
pandas>=1.3.0      # Manejo de datos CSV
numpy>=1.21.0      # Operaciones numéricas
dash>=2.0.0        # Interfaz web (solo para realtime_3d.py)
```

## 🚀 **Instalación y Ejecución**

### **Instalación**:
```bash
pip install -r requirements.txt
```

### **Ejecución Recomendada**:
```bash
python realtime_3d.py
```
- Abre navegador en `http://127.0.0.1:8081`
- Interfaz web interactiva
- Control en tiempo real

### **Ejecución Básica**:
```bash
python main.py
```
- Simulación sin interfaz web
- Visualización estática

## 🔧 **Configuración Avanzada**

### **Modificar Comportamiento**:
1. Editar archivos CSV en `data/`
2. Modificar variables en `config.py`
3. Reiniciar simulación

### **Personalizar Visualización**:
- Cambiar colores en `config.py`
- Modificar tamaños de cubos
- Ajustar opacidades
- Seleccionar tipo de visualización de monstruos

### **Ajustar Parámetros de Simulación**:
- Tamaño del mundo
- Número de agentes
- Frecuencias de acción
- Límites de memoria

## 📚 **Documentación de Reglas**

### **Reglas de Robots (35 reglas)**:
- **Regla 1**: Destrucción cuando hay monstruo en celda actual
- **Regla 2**: Movimiento hacia adelante cuando no hay obstáculos
- **Reglas 3-7**: Movimiento en direcciones específicas según monstruos detectados
- **Reglas 12-16**: Movimiento aleatorio entre dos direcciones
- **Reglas 24-27**: Movimiento aleatorio entre tres direcciones
- **Regla 32**: Movimiento aleatorio entre cuatro direcciones
- **Regla 34**: Rotación aleatoria cuando detecta otro robot
- **Regla 35**: Rotación aleatoria cuando detecta zona vacía

### **Reglas de Monstruos (64 reglas)**:
- Basadas en combinaciones de zonas libres/vacías en 6 direcciones
- Acciones probabilísticas según parámetro `p`
- Movimiento aleatorio entre direcciones disponibles

## 🎯 **Características Técnicas**

### **Algoritmos Implementados**:
- **Coincidencia de reglas**: Búsqueda exacta en DataFrames
- **Detección de colisiones**: Validación de posiciones válidas
- **Rotaciones 3D**: Transformaciones matriciales en ejes X, Y, Z
- **Memoria asociativa**: Búsqueda por similitud de percepciones

### **Optimizaciones**:
- **Carga única de reglas**: Almacenamiento en memoria
- **Validación previa**: Verificación de reglas al inicio
- **Logging asíncrono**: No bloquea la simulación
- **Visualización eficiente**: Actualización incremental

## 🤝 **Uso del Sistema**

### **Para Desarrolladores**:
- Modificar reglas en archivos CSV
- Extender funcionalidad en clases principales
- Personalizar visualización
- Agregar nuevos tipos de agentes

### **Para Investigación**:
- Analizar patrones de comportamiento
- Estudiar eficacia de diferentes reglas
- Comparar estrategias de agentes
- Generar datos para machine learning

### **Para Educación**:
- Entender sistemas multiagente
- Aprender sobre percepción-acción
- Visualizar comportamiento emergente
- Experimentar con parámetros

---

*Desarrollado para el examen parcial de Fundamentos de Inteligencia Artificial - MIA-103*

*Sistema completo de simulación 3D con motor de reglas CSV*