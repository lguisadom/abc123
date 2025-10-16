# 🤖 PROMPT NARRADO FINAL PARA CURSOR — ROBOT (Agente Monstruicida)

El agente que vas a ajustar es el **Robot Monstruicida**.  
Este robot forma parte de la simulación tridimensional junto a los monstruos, pero a diferencia de ellos, **posee memoria interna** y **razonamiento simple basado en percepciones locales**.  
Su comportamiento **no se codifica directamente**, sino que se **define completamente** en un archivo externo llamado **`robot_rules.csv`**.  

Ese archivo contiene **todas las combinaciones posibles de percepciones** y la **acción específica** que el robot debe ejecutar en cada situación.  
Por lo tanto, el programa **no debe agregar reglas nuevas**, **no debe alterar decisiones**, y **no debe tener condiciones adicionales fuera de la tabla**.  
El CSV es la **única fuente de verdad del comportamiento del robot**.

---

## 🧠 Naturaleza y propósito del robot

El robot Monstruicida es un agente con memoria interna.  
Su misión es detectar y eliminar monstruos dentro del entorno, evitando zonas vacías y coordinándose correctamente cuando detecta otro robot.  

El robot tiene sensores que le permiten percibir su entorno de forma relativa a su propia orientación.  
Esto significa que las direcciones **front**, **left**, **right**, **top**, **down** y **behind** no son coordenadas globales, sino direcciones relativas a su posición y orientación actual.  
El código deberá interpretar esas direcciones de manera coherente según la orientación del robot, pero **las reglas que determinan su comportamiento están todas en el archivo CSV**.

---

## ⚙️ Percepciones del robot

El robot dispone de varios sensores que determinan su percepción en cada iteración:

- **Energómetro:** detecta si hay un monstruo en la misma celda.  
- **Monstroscopio:** detecta monstruos adyacentes en sus cinco lados visibles (front, left, right, top, down).  
- **Vacuscopio:** detecta cuando intenta avanzar hacia una zona vacía (valor `-1` si chocó previamente).  
- **Roboscanner:** detecta si hay otro robot al frente.  

Cada percepción tiene un valor que se almacena en el CSV, y todas las combinaciones posibles de percepciones están cubiertas por las reglas de la tabla.

---

## 🧩 Archivo de comportamiento: `robot_rules.csv`

Este archivo define las reglas de decisión del robot.  
Cada fila del CSV representa una combinación perceptual y la acción que corresponde ejecutar.  

El formato del CSV es el siguiente:

| Columna | Descripción |
|----------|-------------|
| `Regla` | Número de regla |
| `Energometro` | 1 si hay monstruo en la misma celda |
| `Lado0_Front`, `Lado1_Top`, `Lado2_Left`, `Lado3_Right`, `Lado4_Down` | Indican presencia de monstruos adyacentes |
| `Vacuoscopio_Front` | 0 si libre, -1 si detectó zona vacía previamente |
| `Roboscanner_Front` | 0 si no hay robot, 1 si hay robot frente a él |
| `Accion` | JSON–like string que describe qué debe hacer el robot |

Ejemplo de valores en la columna **Accion**:

```json
{"tipo": "move", "directions": ["front"]}
{"tipo": "move_random", "directions": ["left", "right"], "probability": 0.5}
{"tipo": "destroy"}
{"tipo": "idle"}
{"tipo": "memory", "notes": "avoid_previous_empty"}
```

---

## 🎯 Comportamiento funcional

1. En cada iteración, el robot **percibe su entorno local** según sus sensores.  
2. El código debe **leer el archivo `robot_rules.csv`**, **buscar la fila que coincide con las percepciones actuales**,  
   y **ejecutar exactamente la acción descrita en la columna `Accion`**.  
3. Si la acción contiene varias direcciones (`"move_random"`), el robot debe **elegir una al azar**,  
   respetando el valor de `"probability"` como probabilidad uniforme.  
4. Si la acción es `"destroy"`, el robot y el monstruo se eliminan, convirtiendo la celda en zona vacía.  
5. Si la acción es `"memory"`, el robot recuerda que en la iteración anterior chocó con una zona vacía y actuará en consecuencia según la tabla.  
6. Si la acción es `"idle"`, simplemente no se mueve en esa iteración.

---

## 🕓 Control temporal y probabilidad

El robot no actúa en cada iteración del simulador.  
Existen dos parámetros globales, **K** y **p**, que se gestionan a nivel de código (no en la tabla):

- **K:** determina cada cuántas iteraciones puede ejecutar una acción.  
- **p:** define la probabilidad de que efectivamente actúe en ese turno.  

El robot solo debe actuar si se cumplen esas condiciones, y cuando lo haga, la acción que ejecuta se obtiene **únicamente del archivo CSV**.

---

## 🔄 Naturaleza probabilística controlada

Cuando una regla del CSV incluye múltiples direcciones posibles, no se trata de una acción aleatoria sin propósito,  
sino de una **decisión probabilística controlada**.  
El robot tiene varios caminos válidos según sus sensores,  
y elige uno de forma aleatoria con igual probabilidad (por ejemplo, `1/3` si hay tres caminos).  
Esa probabilidad está indicada explícitamente en el campo `"probability"` del JSON.

---

## 🧠 Resumen que Cursor debe recordar

- El robot **no inventa reglas**.  
- El comportamiento está completamente descrito en `robot_rules.csv`.  
- El código **solo interpreta y ejecuta** lo que indica la columna `Accion`.  
- Las direcciones son relativas al propio robot.  
- `K` y `p` determinan **cuándo** y **si** actúa, no **qué** hace.  
- Las reglas cubren todos los casos posibles, incluyendo:  
  - Destrucción de monstruo (`"destroy"`).  
  - Movimiento determinista o aleatorio (`"move"` / `"move_random"`).  
  - Inactividad (`"idle"`).  
  - Memoria de zona vacía (`"memory"`).  

---

## 🧩 En resumen para Cursor

> El robot Monstruicida es un agente con memoria interna y percepciones relativas.  
> Todo su comportamiento se define en el archivo `robot_rules.csv`.  
> El código debe leer ese archivo, encontrar la regla que coincide con sus percepciones,  
> y ejecutar exactamente la acción que allí se indica.  
> Si la acción incluye varias direcciones, debe elegir una al azar según la probabilidad indicada.  
> El robot no agrega reglas, no improvisa y no toma decisiones fuera de lo definido en la tabla.  
