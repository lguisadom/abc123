# FUNDAMENTOS DE INTELIGENCIA ARTIFICIAL – MIA-103  
## EXAMEN PARCIAL  
**Domingo 12 de octubre del 2025**

---

### Instrucciones Generales

- Desarrolle el siguiente examen de forma grupal.  
- Fecha de entrega: **viernes 17 de octubre del 2025**.  
- Elabore todos los procedimientos en **Google Colab con Python**.  
- Todos los datos y código fuente deben estar almacenados en **Google Drive**.  

#### Productos del examen:
1. Documento donde se expone el procedimiento de solución al problema.  
2. Programas fuente en Python.  
3. Procedimiento de ejecución del algoritmo.  
4. Datos recolectados y sus respectivas transformaciones.  
5. Fuentes bibliográficas recolectadas.  
6. Todos los elementos deben estar disponibles en una dirección de Google Drive.

---

## 1. ENTORNO DE OPERACIÓN

Considere un entorno conformado por **N³ cubos** de lado N (hexaedro regular).  
El entorno es energético, no físico, y contiene:

- **Zonas Libres (0):** cubos donde pueden ubicarse entidades (robots, monstruos).  
- **Zonas Vacías (-1):** cubos imposibles de atravesar por entidades materiales o energéticas.  
  - El entorno está rodeado de zonas vacías (frontera).  

Los agentes sólo perciben el entorno mediante sensores.

Parámetros iniciales:
- `N`: tamaño del lado.  
- `Pfree`: porcentaje de zonas libres.  
- `Psoft`: porcentaje de zonas vacías.  
- `Nrobot`: número de robots (instancias del agente robot).  
- `Nmonstruos`: número de monstruos (instancias del agente monstruo).  

El entorno debe crearse **aleatoriamente** al ejecutar el programa.

---

## 2. ENTIDADES EN EL ENTORNO

### 2.1 ROBOT

Los robots **Monstruicidas** operan dentro del entorno.  
Su objetivo es **cazar monstruos**.

- Las zonas vacías no se detectan desde lejos.  
- Solo pueden detectarse al **intentar avanzar** y fallar (usando el *Vacuscopio*).  
- Los robots se comunican entre sí en casos específicos.  
- Cada robot tiene sus propias reglas y memoria independiente.

#### 2.1.1 SENSORES

1. **Giroscopio:** define orientación en el espacio.  
   - Indica dirección, no posición.  
2. **Monstroscopio:** detecta la existencia de monstruos en las celdas vecinas (5 lados, sin el posterior).  
3. **Vacuscopio:** se activa al chocar con una zona vacía; registra el evento.  
4. **Energómetro espectral:** detecta la existencia de monstruos en la celda actual.  
5. **Roboscanner:** detecta si delante existe otro robot.  
   - Si dos robots se encuentran, pueden decidir:
     - Ambos rotan 90°.  
     - Uno sigue recto y el otro rota 90°.

> El robot no conoce su ubicación absoluta, solo su orientación actual y su última posición (memoria interna).

---

#### 2.1.2 EFECTORES

1. **Propulsor direccional:** mueve al robot hacia su frente.  
   - Si detecta zona vacía → activa el Vacuscopio.  
2. **Reorientador:** permite rotar 90° hacia alguno de sus 4 lados.  
3. **Vacuumatór:** destruye un monstruo y convierte su cubo en zona vacía.

---

#### 2.1.3 MEMORIA INTERNA

El robot guarda sus percepciones y acciones históricas:
- Registra el tiempo, percepción y acción ejecutada.  
- La memoria es independiente por robot (no se comparte).  
- Si un robot es destruido, su memoria se elimina.

Puede generar **nuevas reglas de decisión** según su experiencia.  
La memoria no es completamente verdadera; puede contener información obsoleta.

---

### 2.2 MONSTRUOS

- Entidades energéticas (sin cuerpo físico).  
- Ocupan completamente un cubo.  
- Irradian energía detectable con el *Monstroscopio*.  
- Pueden moverse a cualquiera de sus 6 celdas vecinas.

#### Para ser destruidos:
1. El robot debe ingresar a la celda del monstruo.  
2. Detectarlo con el **Energómetro**.  
3. Activar el **Vacuumatór**, destruyendo al monstruo y al robot, convirtiendo la celda en zona vacía.

#### Comportamiento:
- Actúan como **agentes reflejo simples**.  
- Cada K iteraciones, tienen probabilidad p de moverse aleatoriamente a una celda libre (sin entrar en zona vacía).  
- No comunican su movimiento a los robots.

---

## 3. REPRESENTACIÓN DEL CONOCIMIENTO

1. Identificar elementos conceptuales del entorno.  
2. Definir conceptos ontológicos con claridad.  
3. Representar entidades y relaciones en el entorno (ontología).  
4. Identificar elementos no explícitos del enunciado.  

---

## 4. OBJETIVO

Construir los **dos agentes** (Robot y Monstruo) para operar en el entorno tridimensional.

### 4.1 ROBOT
- Implementar el robot como **agente con memoria interna**.  
- Puede generar nuevas reglas según su experiencia.  
- Puede establecer jerarquías de reglas (criterios adicionales).  

### 4.2 MONSTRUO
- Implementar el monstruo como **agente reflejo simple**, con frecuencia de operación diferente al robot.

---

## 5. PROCEDIMIENTO

### 5.1 ONTOLOGÍA
- Establecer lista de conceptos ontológicos y sus relaciones.

### 5.2 EL PROBLEMA
- Definir el problema a resolver según las definiciones ontológicas.  
- No formularlo como pregunta.

### 5.3 REPRESENTACIÓN DEL CONOCIMIENTO

#### 5.3.1 Entidades operativas
- Identificar todas las entidades que operan en el entorno.

#### 5.3.2 Agentes
- Describir los agentes: definición, características, percepciones, acciones.

#### 5.3.3 Percepciones de cada entidad
- Ejemplos de percepciones y sus combinaciones posibles.

#### 5.3.4 Acciones de cada entidad
- Ejemplos de acciones resultantes según percepciones.

#### 5.3.5 Medio ambiente
Clasificar el entorno según criterios del AIMA:
- Accesible / no accesible.  
- Determinista / no determinista.  
- Episódico / no episódico.  
- Estático / dinámico.  
- Discreto / continuo.

#### 5.3.6 Tabla percepción–acción
- Definir tabla de cada agente.  
- Para el robot, la tabla es **referencial** (usa memoria y aprendizaje).  
- El monstruo usa **tabla fija (reflejo simple)**.  
- Incluir acciones aleatorias solo cuando se encuentra con otro robot.

#### 5.3.7 Mapeo percepción–acción
- Describir cómo el robot almacena y usa su memoria de percepciones y acciones históricas.

#### 5.3.8 Frecuencia de operación
- Robot: 1 percepción por segundo.  
- Monstruo: 1 operación cada **K segundos**.

#### 5.3.9 Racionalidad del agente
- Definir una medida de racionalidad del robot.

#### 5.3.10 Ambiente episódico
- Explicar si el agente robot es episódico.  
- Analizar si entra en bucle infinito.

---

## 5.4 CONSTRUCCIÓN DE LOS AGENTES

### 5.4.1 Sistema de información
- Implementar en Python el entorno de operación y la visualización del entorno y los agentes.

### 5.4.2 Agentes inteligentes
- Implementar en Python los agentes, su lógica y resultados.  
- Exponer diseño técnico del agente (clases, funciones, variables).  
- Documentar cómo se implementó cada componente.

---

## 5.5 PRUEBAS DEL PROCEDIMIENTO
- Presentar ejemplos de ejecuciones.  
- Mostrar evidencia verificable de que el procedimiento cumple el objetivo.

## 5.6 ANÁLISIS DE RESULTADOS
- Presentar resultados y análisis de las ejecuciones.  
- Mostrar evidencia visual o tabular de los elementos de la representación del conocimiento.

---
