# 🤖 Simulación Robots Monstruicidas vs Monstruos

## 📋 Descripción del Proyecto

Este proyecto implementa una simulación 3D completa de robots monstruicidas que cazan monstruos en un entorno energético tridimensional, desarrollado para el examen parcial del curso "Fundamentos de Inteligencia Artificial - MIA-103".

## 🏗️ Estructura del Proyecto

```
examen-parcial/
├── main.py                    # Script principal de simulación básica
├── realtime_3d.py             # Simulación interactiva con interfaz web (RECOMENDADO)
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
- 🌐 **Interfaz web interactiva** con Dash
- ⏯️ **Control en tiempo real** (pausa, paso a paso, reinicio)
- 📊 **Visualización 3D interactiva** con Plotly

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
dash>=2.0.0
```

**Nota:** `dash` es necesario para la interfaz web interactiva de `realtime_3d.py`

### 🚀 **Ejecución**

#### 📱 **Simulación en Tiempo Real (Recomendado)**

Para ejecutar la simulación interactiva con interfaz web:

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar simulación en tiempo real
python realtime_3d.py
```

**Características de la simulación en tiempo real:**
- 🌐 Interfaz web en `http://127.0.0.1:8081`
- ⏯️ Control paso a paso o ejecución continua
- 🔄 Reinicio de simulación en tiempo real
- 📊 Visualización 3D interactiva con Plotly
- 📝 Logs detallados en consola

#### 🖥️ **Simulación Básica**

Para ejecutar la simulación básica sin interfaz web:

```bash
# Ejecutar simulación básica
python main.py
```

#### 🪟 **Recomendaciones para Windows**

**Opción 1: Usando PowerShell (Recomendado)**
1. **Instalar Python 3.8+** desde [python.org](https://python.org)
2. **Abrir PowerShell** como administrador
3. **Navegar al directorio del proyecto:**
   ```powershell
   cd C:\ruta\a\tu\proyecto\examen-parcial
   ```
4. **Instalar dependencias:**
   ```powershell
   pip install plotly pandas numpy dash
   ```
5. **Ejecutar la simulación:**
   ```powershell
   python realtime_3d.py
   ```
6. **Abrir navegador** en `http://127.0.0.1:8081`

**Opción 2: Usando CMD**
1. **Abrir CMD** como administrador
2. **Navegar al directorio:**
   ```cmd
   cd C:\ruta\a\tu\proyecto\examen-parcial
   ```
3. **Instalar dependencias:**
   ```cmd
   pip install plotly pandas numpy dash
   ```
4. **Ejecutar simulación:**
   ```cmd
   python realtime_3d.py
   ```

**Opción 3: Usando Visual Studio Code**
1. **Abrir VS Code** y abrir la carpeta del proyecto
2. **Abrir terminal integrado** (Ctrl + `)
3. **Ejecutar comandos:**
   ```bash
   pip install plotly pandas numpy dash
   python realtime_3d.py
   ```

**⚠️ Problemas comunes en Windows:**
- Si `python` no funciona, usar `py` o `python3`
- Si hay problemas de permisos, ejecutar como administrador
- Si el puerto 8081 está ocupado, cambiar el puerto en `realtime_3d.py`

#### ☁️ **Recomendaciones para Google Colab**

1. **Subir archivos** al Colab:
   ```python
   # Subir archivos necesarios
   from google.colab import files
   uploaded = files.upload()
   ```

2. **Instalar dependencias:**
   ```python
   !pip install plotly pandas numpy dash
   ```

3. **Ejecutar simulación:**
   ```python
   !python realtime_3d.py
   ```

4. **Acceder a la interfaz web:**
   - Usar `ngrok` para exponer el puerto:
   ```python
   !pip install pyngrok
   from pyngrok import ngrok
   
   # Exponer puerto 8081
   public_url = ngrok.connect(8081)
   print(f"Accede a: {public_url}")
   ```

#### 🐧 **Recomendaciones para Linux/macOS**

```bash
# Instalar dependencias
pip3 install -r requirements.txt

# Ejecutar simulación
python3 realtime_3d.py

# Abrir navegador automáticamente
xdg-open http://127.0.0.1:8081  # Linux
open http://127.0.0.1:8081      # macOS
```

#### 🔧 **Comandos Útiles**

```bash
# Ver documentación
ls docs/

# Ejecutar con logs detallados
python realtime_3d.py --verbose

# Ejecutar simulación paso a paso
python realtime_3d.py --step-by-step
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