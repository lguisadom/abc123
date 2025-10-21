#!/usr/bin/env python3
"""
Módulo Robot - Implementación del agente Robot con sistema de reglas CSV
Contiene la clase Robot con sensores, memoria y comportamiento basado en reglas
"""

import random
import json
from typing import List, Tuple, Dict, Any, Optional
from config import ROBOT_FREQUENCY, ROBOT_MEMORY_LIMIT
from console_formatter import console

class Robot:
    """
    Agente Robot Monstruicida que opera en el entorno 3D
    Tiene sensores, memoria interna y comportamiento basado en reglas CSV
    """
    
    def __init__(self, robot_id: int, position: Tuple[int, int, int], environment, rule_engine=None, logger=None):
        """
        Inicializa un robot
        
        Args:
            robot_id: Identificador único del robot
            position: Posición inicial (x, y, z)
            environment: Referencia al entorno
            rule_engine: Motor de reglas para comportamiento
            logger: Sistema de logging para operaciones
        """
        self.id = robot_id
        self.id_formatted = f"R{robot_id:03d}"  # Formato R001, R002, etc.
        self.position = list(position)  # Convertir a lista para mutabilidad
        self.environment = environment
        self.rule_engine = rule_engine
        self.logger = logger
        
        # Estado del robot
        self.orientation = [0, 0, 1]  # Vector de orientación (frente hacia +Z)
        self.alive = True
        self.monsters_destroyed = 0  # Contador de monstruos destruidos
        self.robots_collided = 0  # Contador de robots eliminados por colisión
        
        # Sensores (estructura para reglas CSV)
        self.sensors = {
            'Energometro': 0,         # Monstruo en celda actual (0=no, 1=sí)
            'Lado1_Top': 0,          # Monstruo arriba (↑ X+90°) (0=no, 1=sí)
            'Lado2_Left': 0,         # Monstruo a la izquierda (← Y+90°) (0=no, 1=sí)
            'Vacuoscopio_Front': 0,   # Zona vacía al frente (0=libre, -1=vacía)
            'Lado0_Front': 0,         # Monstruo al frente (▲ Z+90°) (0=no, 1=sí)
            'Roboscanner_Front': 0,   # Robot al frente (0=no, 2=sí)
            'Lado3_Right': 0,        # Monstruo a la derecha (→ Y-90°) (0=no, 1=sí)
            'Lado4_Down': 0,         # Monstruo abajo (↓ X-90°) (0=no, 1=sí)
        }
        
        # Memoria interna
        self.memory = []
        self.memory_limit = ROBOT_MEMORY_LIMIT
        self.previous_position = None  # Para memoria de zona vacía
        self.collided_with_empty = False  # Flag para memoria de colisión
        self.vacuscope_memory = 0  # Memoria temporal del Vacuoscopio (-1 si chocó con zona vacía)
        
        # Parámetros de comportamiento
        self.frequency = ROBOT_FREQUENCY
        self.steps_since_last_action = 0
        
        # Registrar robot en el entorno
        self.environment.register_robot(self.id, tuple(self.position))
    
    def perceive(self, resetVacuscopeMemory = True) -> Dict[str, Any]:
        """
        Realiza la percepción del entorno usando todos los sensores
        Actualiza los valores de los sensores basándose en el estado actual
        
        Returns:
            Dict con la percepción actual del robot
        """
        if not self.alive:
            return {}
        
        x, y, z = self.position
        
        # Actualizar Energómetro (detecta monstruos en la celda actual)
        current_position = (x, y, z)
        if self.environment.is_monster_at(current_position):
            self.sensors['Energometro'] = 1  # Hay monstruo en la celda actual
        else:
            self.sensors['Energometro'] = 0  # No hay monstruo en la celda actual
        
        # Actualizar Monstroscopio (detección de monstruos en 5 direcciones)
        self._update_monstroscope(x, y, z)
        
        # Actualizar Vacuscopio (detección de zonas vacías al frente)
        self._update_vacuscope(x, y, z)
        
        # Actualizar Roboscanner (detección de otros robots al frente)
        self._update_roboscanner(x, y, z)
        
        # NO resetear aquí - se resetea después de act() para que pueda usar la información
        
        return self.sensors.copy()
    
    def _update_monstroscope(self, x: int, y: int, z: int):
        """
        Actualiza la detección de monstruos en las 5 direcciones según el orden de la imagen
        """
        # Mapeo: Lado1_Top, Lado2_Left, Lado0_Front, Lado3_Right, Lado4_Down
        directions = {
            'Lado1_Top': self._get_up_position(x, y, z),      # ↑ X+90°
            'Lado2_Left': self._get_left_position(x, y, z),   # ← Y+90°
            'Lado0_Front': self._get_front_position(x, y, z), # ▲ Z+90°
            'Lado3_Right': self._get_right_position(x, y, z), # → Y-90°
            'Lado4_Down': self._get_down_position(x, y, z)   # ↓ X-90°
        }
        
        for sensor_name, pos in directions.items():
            if pos and self.environment.is_monster_at(pos):
                self.sensors[sensor_name] = 1
            else:
                self.sensors[sensor_name] = 0
    
    def _update_vacuscope(self, x: int, y: int, z: int):
        """
        Actualiza la detección de zonas vacías al frente usando memoria temporal
        """
        # Usar la memoria temporal del Vacuoscopio si existe
        if self.vacuscope_memory == -1:
            self.sensors['Vacuoscopio_Front'] = -1  # Usar memoria de colisión previa
        else:
            self.sensors['Vacuoscopio_Front'] = 0   # Zona libre
    
    def _update_roboscanner(self, x: int, y: int, z: int):
        """
        Actualiza la detección de otros robots al frente
        """
        front_pos = self._get_front_position(x, y, z)
        
        if front_pos and self.environment.is_robot_at(front_pos, self.id):
            self.sensors['Roboscanner_Front'] = 2  # Robot detectado
            # Manejar encuentro con robot
            self._handle_robot_encounter(front_pos)
        else:
            self.sensors['Roboscanner_Front'] = 0  # No hay robot
    
    def _get_direction_index(self, direction: str) -> int:
        """
        Obtiene el índice de dirección
        """
        direction_map = {
            'Front': 0,
            'Top': 1,
            'Left': 2,
            'Right': 3,
            'Down': 4
        }
        return direction_map.get(direction, 0)
    
    def _handle_robot_encounter(self, other_robot_position: Tuple[int, int, int]):
        """
        Maneja el encuentro con otro robot
        """
        # Encontrar el ID del otro robot
        other_robot_id = None
        for robot_id, robot_pos in self.environment.robot_positions.items():
            if robot_pos == other_robot_position and robot_id != self.id:
                other_robot_id = robot_id
                break
        
        if other_robot_id is not None:
            console.info(f"Robots {self.id} y {other_robot_id} se encontraron en {other_robot_position}")
            # Implementar lógica de comunicación según especificaciones
            self._rotate_y_positive()  # Rotar hacia la izquierda (y+90)
            console.info(f"Robot {self.id} giró a la izquierda debido al encuentro")
    
    def _get_front_position(self, x: int, y: int, z: int) -> Optional[Tuple[int, int, int]]:
        """Obtiene la posición al frente según la orientación"""
        ox, oy, oz = self.orientation
        new_x, new_y, new_z = x + ox, y + oy, z + oz
        
        # Siempre retornar la posición, sin importar si es válida o no
        # para que el Vacuscopio pueda detectar zonas vacías
        return (new_x, new_y, new_z)
    
    def _get_backward_position(self, x: int, y: int, z: int) -> Optional[Tuple[int, int, int]]:
        """Obtiene la posición hacia atrás según la orientación"""
        ox, oy, oz = self.orientation
        new_x, new_y, new_z = x - ox, y - oy, z - oz
        
        # Siempre retornar la posición, sin importar si es válida o no
        # para que el Vacuscopio pueda detectar zonas vacías
        return (new_x, new_y, new_z)
    
    def _get_left_position(self, x: int, y: int, z: int) -> Optional[Tuple[int, int, int]]:
        """Obtiene la posición a la izquierda según la orientación"""
        # Rotar orientación 90 grados a la izquierda
        ox, oy, oz = self.orientation
        left_orientation = self._rotate_left(ox, oy, oz)
        new_x, new_y, new_z = x + left_orientation[0], y + left_orientation[1], z + left_orientation[2]
        
        # Siempre retornar la posición para detectar zonas vacías
        return (new_x, new_y, new_z)
    
    def _get_right_position(self, x: int, y: int, z: int) -> Optional[Tuple[int, int, int]]:
        """Obtiene la posición a la derecha según la orientación"""
        # Rotar orientación 90 grados a la derecha
        ox, oy, oz = self.orientation
        right_orientation = self._rotate_right(ox, oy, oz)
        new_x, new_y, new_z = x + right_orientation[0], y + right_orientation[1], z + right_orientation[2]
        
        # Siempre retornar la posición para detectar zonas vacías
        return (new_x, new_y, new_z)
    
    def _get_up_position(self, x: int, y: int, z: int) -> Optional[Tuple[int, int, int]]:
        """Obtiene la posición arriba"""
        new_x, new_y, new_z = x, y, z + 1
        
        # Siempre retornar la posición para detectar zonas vacías
        return (new_x, new_y, new_z)
    
    def _get_down_position(self, x: int, y: int, z: int) -> Optional[Tuple[int, int, int]]:
        """Obtiene la posición abajo"""
        new_x, new_y, new_z = x, y, z - 1
        
        # Siempre retornar la posición para detectar zonas vacías
        return (new_x, new_y, new_z)
    
    def _rotate_left(self, ox: int, oy: int, oz: int) -> List[int]:
        """Rota el vector de orientación 90 grados a la izquierda"""
        # Rotación simple en el plano XY
        return [-oy, ox, oz]
    
    def _rotate_right(self, ox: int, oy: int, oz: int) -> List[int]:
        """Rota el vector de orientación 90 grados a la derecha"""
        # Rotación simple en el plano XY
        return [oy, -ox, oz]
    
    def act(self, perceptions: Dict[str, Any], monsters_list=None) -> str:
        """
        Decide una acción basada en las percepciones usando el motor de reglas
        NO ejecuta la acción, solo la decide
        
        Args:
            perceptions: Diccionario con las percepciones
            monsters_list: Lista de monstruos para acciones de destrucción
            
        Returns:
            str: Acción decidida (no ejecutada)
        """
        if not self.alive:
            return "none"
        
        # Guardar estado inicial para logging
        initial_position = tuple(self.position)
        initial_orientation = self.orientation.copy()
        
        # VERIFICAR SI ES REGLA 35 (zona vacía al frente) - SIEMPRE PREVALECE
        is_rule_35 = perceptions.get('Vacuoscopio_Front', 0) == -1
        
        # Inicializar variables
        memory_action = None
        uses_memory = 0
        uses_rule = 1
        
        if is_rule_35:
            # REGLA 35 SIEMPRE PREVALECE - No consultar memoria
            if self.rule_engine:
                action = self.rule_engine.get_robot_action(perceptions)
                rule_num = self.rule_engine.get_robot_rule_number(perceptions)
            else:
                action = self._default_behavior(perceptions)
                rule_num = 0
            uses_memory = 0
            uses_rule = 1
            console.info(f"🚨 Robot {self.id_formatted} usa REGLA #{rule_num} (ZONA VACÍA - PREVALECE): {action}")
        else:
            # CONSULTAR MEMORIA PRIMERO (solo si NO es regla 35)
            memory_action = self.consult_memory(perceptions)
            
            if memory_action is not None:
                # Usar acción de la memoria
                action = memory_action
                rule_num = 0  # No se aplicó regla
                uses_memory = 1
                uses_rule = 0
                console.info(f"🧠 Robot {self.id_formatted} usa MEMORIA: {action}")
            else:
                # Usar motor de reglas si está disponible
                if self.rule_engine:
                    action = self.rule_engine.get_robot_action(perceptions)
                    rule_num = self.rule_engine.get_robot_rule_number(perceptions)
                else:
                    # Comportamiento por defecto si no hay motor de reglas
                    action = self._default_behavior(perceptions)
                    rule_num = 0
                console.info(f"📋 Robot {self.id_formatted} usa REGLA #{rule_num}: {action}")
        
        # Calcular nueva posición y orientación después de la acción
        new_position, new_orientation, executed_direction = self._calculate_new_state(action)
        
        # Convertir acción probabilística a específica si es necesario
        specific_action = self._convert_to_specific_action(action, initial_orientation, new_orientation, executed_direction)
        
        # Guardar datos para logging (solo almacenar, no escribir aún)
        if self.logger:
            operation_data = {
                'position': initial_position,
                'orientation': initial_orientation,
                'sensors': perceptions,
                'rule_num': rule_num,
                'action': action,  # Usar la acción original de la regla
                'specific_action': specific_action,  # Usar la acción original de la regla
                'new_position': new_position,
                'new_orientation': new_orientation,
                'memory_action': memory_action or '',
                'uses_memory': uses_memory,
                'uses_rule': uses_rule
            }
            self.logger.store_robot_operation(self.id, operation_data)
        
        # Guardar en memoria - usar la acción específica
        self._save_to_memory(perceptions, specific_action)
        
        # Resetear memoria del Vacuoscopio después de usarla
        if self.vacuscope_memory == -1:
            self.reset_vacuscope_memory()
        
        self.steps_since_last_action = 0
        
        return specific_action  # Retornar la acción específica
    
    def _filter_effective_rotations(self, directions: List[str]) -> List[str]:
        """
        Filtra las rotaciones que realmente cambiarían la orientación actual
        (Necesario debido a problema en la implementación de rotaciones globales)
        
        Args:
            directions: Lista de direcciones disponibles
            
        Returns:
            Lista de direcciones que cambiarían la orientación
        """
        effective_directions = []
        current_orientation = self.orientation
        
        for direction in directions:
            if direction in ['x+90', 'x-90', 'y+90', 'y-90']:
                # Calcular la nueva orientación si se aplicara esta rotación
                ox, oy, oz = current_orientation
                
                if direction == 'x+90':
                    new_orientation = [ox, -oz, oy]
                elif direction == 'x-90':
                    new_orientation = [ox, oz, -oy]
                elif direction == 'y+90':
                    new_orientation = [oz, oy, -ox]
                elif direction == 'y-90':
                    new_orientation = [-oz, oy, ox]
                
                # Solo incluir si la orientación cambiaría
                if new_orientation != current_orientation:
                    effective_directions.append(direction)
            else:
                # Para movimientos (no rotaciones), siempre incluir
                effective_directions.append(direction)
        
        return effective_directions
    
    def _calculate_relative_rotation(self, orientation, rotation_type):
        """
        Calcula rotaciones relativas al movimiento del robot
        Basado en la referencia inicial de la cabeza del robot.
        Las rotaciones SIEMPRE son respecto a la posición inicial de la cabeza.
        
        Definición del usuario:
        - y-90: rotar hacia la derecha (respecto a referencia inicial)
        - y+90: rotar hacia la izquierda (respecto a referencia inicial)
        - x+90: rotar hacia arriba (respecto a referencia inicial)
        - x-90: rotar hacia abajo (respecto a referencia inicial)
        """
        x, y, z = orientation
        
        if rotation_type == 'y-90':  # Rotar hacia la derecha (respecto a referencia inicial)
            if orientation == [0, 1, 0]:  # Cabeza arriba (referencia inicial)
                return [1, 0, 0]  # Derecha
            elif orientation == [0, -1, 0]:  # Cabeza abajo
                return [-1, 0, 0]  # Izquierda
            elif orientation == [1, 0, 0]:  # Cabeza derecha
                return [0, -1, 0]  # Abajo
            elif orientation == [-1, 0, 0]:  # Cabeza izquierda
                return [0, 1, 0]  # Arriba
            elif orientation == [0, 0, 1]:  # Cabeza adelante
                return [1, 0, 0]  # Derecha
            elif orientation == [0, 0, -1]:  # Cabeza atrás
                return [-1, 0, 0]  # Izquierda
        
        elif rotation_type == 'y+90':  # Rotar hacia la izquierda (respecto a referencia inicial)
            if orientation == [0, 1, 0]:  # Cabeza arriba (referencia inicial)
                return [-1, 0, 0]  # Izquierda
            elif orientation == [0, -1, 0]:  # Cabeza abajo
                return [1, 0, 0]  # Derecha
            elif orientation == [1, 0, 0]:  # Cabeza derecha
                return [0, 1, 0]  # Arriba
            elif orientation == [-1, 0, 0]:  # Cabeza izquierda
                return [0, -1, 0]  # Abajo
            elif orientation == [0, 0, 1]:  # Cabeza adelante
                return [-1, 0, 0]  # Izquierda
            elif orientation == [0, 0, -1]:  # Cabeza atrás
                return [1, 0, 0]  # Derecha
        
        elif rotation_type == 'x+90':  # Rotar hacia arriba (respecto a referencia inicial)
            if orientation == [0, 1, 0]:  # Cabeza arriba (referencia inicial)
                return [0, 0, 1]  # Adelante
            elif orientation == [0, -1, 0]:  # Cabeza abajo
                return [0, 0, -1]  # Atrás
            elif orientation == [1, 0, 0]:  # Cabeza derecha
                return [0, 1, 0]  # Arriba
            elif orientation == [-1, 0, 0]:  # Cabeza izquierda
                return [0, -1, 0]  # Abajo
            elif orientation == [0, 0, 1]:  # Cabeza adelante
                return [0, -1, 0]  # Abajo
            elif orientation == [0, 0, -1]:  # Cabeza atrás
                return [0, 1, 0]  # Arriba
        
        elif rotation_type == 'x-90':  # Rotar hacia abajo (respecto a referencia inicial)
            if orientation == [0, 1, 0]:  # Cabeza arriba (referencia inicial)
                return [0, 0, -1]  # Atrás
            elif orientation == [0, -1, 0]:  # Cabeza abajo
                return [0, 0, 1]  # Adelante
            elif orientation == [1, 0, 0]:  # Cabeza derecha
                return [0, -1, 0]  # Abajo
            elif orientation == [-1, 0, 0]:  # Cabeza izquierda
                return [0, 1, 0]  # Arriba
            elif orientation == [0, 0, 1]:  # Cabeza adelante
                return [0, 1, 0]  # Arriba
            elif orientation == [0, 0, -1]:  # Cabeza atrás
                return [0, -1, 0]  # Abajo
        
        return orientation
    
    def _convert_to_specific_action(self, action: str, initial_orientation: List[int], new_orientation: List[int], executed_direction: str) -> str:
        """
        Convierte una acción probabilística en una acción específica basada en la dirección ejecutada
        
        Args:
            action: Acción original (puede contener probabilidades)
            initial_orientation: Orientación inicial antes de la acción
            new_orientation: Nueva orientación después de la acción
            executed_direction: Dirección específica que se ejecutó
            
        Returns:
            Acción específica que realmente se ejecutó
        """
        try:
            action_data = json.loads(action)
            action_type = action_data.get('tipo', '')
            
            if action_type == 'move_random':
                # Usar la dirección específica que se ejecutó
                specific_action = f'{{"tipo": "move", "directions": ["{executed_direction}"]}}'
                return specific_action
            
            else:
                # Para otras acciones, devolver tal como está
                return action
                
        except (json.JSONDecodeError, KeyError):
            # Si no se puede parsear, devolver la acción original
            return action
    
    def _calculate_z_forward_position(self) -> Tuple[int, int, int]:
        """Calcula la nueva posición si se avanzara en Z, verificando obstáculos"""
        x, y, z = self.position
        new_position = (x, y, z + 1)
        
        # Verificar si la nueva posición es válida (sin obstáculos)
        if self.environment.is_valid_position(*new_position):
            return new_position
        else:
            # No puede avanzar, mantener posición actual
            return tuple(self.position)
    
    def _calculate_z_backward_position(self) -> Tuple[int, int, int]:
        """Calcula la nueva posición si se retrocediera en Z, verificando obstáculos"""
        x, y, z = self.position
        new_position = (x, y, z - 1)
        
        # Verificar si la nueva posición es válida (sin obstáculos)
        if self.environment.is_valid_position(*new_position):
            return new_position
        else:
            # No puede retroceder, mantener posición actual
            return tuple(self.position)
    
    def _calculate_new_state(self, action: str) -> Tuple[Tuple[int, int, int], List[int], str]:
        """
        Calcula la nueva posición y orientación que tendría el robot después de ejecutar la acción
        Sin ejecutar realmente la acción
        
        Args:
            action: Acción a simular
            
        Returns:
            Tuple con (nueva_posición, nueva_orientación, dirección_ejecutada)
        """
        try:
            action_data = json.loads(action)
            action_type = action_data.get('tipo')
            
            new_position = tuple(self.position)
            new_orientation = self.orientation.copy()
            executed_direction = "none"  # Dirección específica ejecutada
            
            if action_type == 'destroy':
                # La posición y orientación no cambian al destruir
                pass
            elif action_type == 'memory':
                # Retroceder de zona vacía - simular movimiento hacia atrás
                new_position = self._get_backward_position(*self.position)
                executed_direction = "back"
            elif action_type == 'idle':
                # No cambiar posición ni orientación
                pass
            elif action_type == 'move':
                directions = action_data.get('directions', [])
                if directions:
                    direction = directions[0]
                    executed_direction = direction
                    if direction == 'z+90':
                        new_position = self._calculate_z_forward_position()
                    # MANEJAR ROTACIONES EN MOVE
                    elif direction == 'x+90':
                        # Rotación hacia arriba (relativa al robot)
                        new_orientation = self._calculate_relative_rotation(self.orientation, 'x+90')
                    elif direction == 'x-90':
                        # Rotación hacia abajo (relativa al robot)
                        new_orientation = self._calculate_relative_rotation(self.orientation, 'x-90')
                    elif direction == 'y+90':
                        # Rotación hacia la izquierda (relativa al robot)
                        new_orientation = self._calculate_relative_rotation(self.orientation, 'y+90')
                    elif direction == 'y-90':
                        # Rotación hacia la derecha (relativa al robot)
                        new_orientation = self._calculate_relative_rotation(self.orientation, 'y-90')
            elif action_type == 'move_random':
                directions = action_data.get('directions', [])
                if directions:
                    # Filtrar rotaciones que no cambiarían la orientación (problema de implementación)
                    effective_directions = self._filter_effective_rotations(directions)
                    
                    if effective_directions:
                        # Seleccionar dirección aleatoria de las efectivas
                        direction = random.choice(effective_directions)
                    else:
                        # Si no hay rotaciones efectivas, usar la primera disponible
                        direction = directions[0]
                    
                    executed_direction = direction
                    if direction == 'z+90':
                        new_position = self._calculate_z_forward_position()
                    # MANEJAR ROTACIONES
                    elif direction == 'x+90':
                        # Rotación hacia arriba (relativa al robot)
                        new_orientation = self._calculate_relative_rotation(self.orientation, 'x+90')
                    elif direction == 'x-90':
                        # Rotación hacia abajo (relativa al robot)
                        new_orientation = self._calculate_relative_rotation(self.orientation, 'x-90')
                    elif direction == 'y+90':
                        # Rotación hacia la izquierda (relativa al robot)
                        new_orientation = self._calculate_relative_rotation(self.orientation, 'y+90')
                    elif direction == 'y-90':
                        # Rotación hacia la derecha (relativa al robot)
                        new_orientation = self._calculate_relative_rotation(self.orientation, 'y-90')
            elif action_type == 'rotate':
                directions = action_data.get('directions', [])
                if directions:
                    direction = directions[0]
                    executed_direction = direction
                    if direction == 'left':
                        new_orientation = self._rotate_left(*self.orientation)
                    elif direction == 'right':
                        new_orientation = self._rotate_right(*self.orientation)
                    elif direction == 'x+90':
                        # Rotación hacia arriba (relativa al robot)
                        new_orientation = self._calculate_relative_rotation(self.orientation, 'x+90')
                    elif direction == 'x-90':
                        # Rotación hacia abajo (relativa al robot)
                        new_orientation = self._calculate_relative_rotation(self.orientation, 'x-90')
                elif direction == 'y+90':
                    # Rotación hacia la izquierda (relativa al robot)
                    new_orientation = self._calculate_relative_rotation(self.orientation, 'y+90')
                elif direction == 'y-90':
                    # Rotación hacia la derecha (relativa al robot)
                    new_orientation = self._calculate_relative_rotation(self.orientation, 'y-90')
            
            return new_position, new_orientation, executed_direction
            
        except (json.JSONDecodeError, KeyError, IndexError):
            # Si hay error en la acción, no cambiar estado
            return tuple(self.position), self.orientation.copy(), "none"
    
    def execute_action(self, action: str, monsters_list=None, monster_logger=None):
        """
        Ejecuta la acción especificada
        
        Args:
            action: Acción a ejecutar
            monsters_list: Lista de monstruos para acciones de destrucción
            monster_logger: Logger de monstruos para registrar muertes
        """
        self._execute_action(action, monsters_list, monster_logger)
    
    def _default_behavior(self, perceptions: Dict[str, Any]) -> str:
        """
        Comportamiento por defecto cuando no hay motor de reglas
        """
        # Comportamiento simple por defecto
        if perceptions.get('Lado0_Front', 0) == 1:
            return '{"tipo": "move", "directions": ["z+90"]}'
        elif perceptions.get('Vacuoscopio_Front', 0) == -1:
            return '{"tipo": "memory", "notes": "avoid_previous_empty"}'
        else:
            return '{"tipo": "move", "directions": ["z+90"]}'
    
    def _execute_action(self, action: str, monsters_list=None, monster_logger=None):
        """
        Ejecuta la acción especificada según el formato JSON
        """
        try:
            # Parsear la acción JSON
            action_data = json.loads(action)
            action_type = action_data.get('tipo')
            
            if action_type == 'destroy':
                self._destroy_monster(monsters_list, monster_logger)
            elif action_type == 'memory':
                self._step_back_from_empty()
            elif action_type == 'idle':
                # No hacer nada
                pass
            elif action_type == 'move':
                directions = action_data.get('directions', [])
                if directions:
                    self._move_in_direction(directions[0])
            elif action_type == 'move_random':
                directions = action_data.get('directions', [])
                if directions:
                    # Usar la primera dirección (ya fue elegida aleatoriamente en act())
                    self._move_in_direction(directions[0])
            else:
                console.warning(f"Tipo de acción no reconocido: {action_type}")
                
        except json.JSONDecodeError as e:
            console.error(f"Error parseando acción JSON: {e}")
            console.error(f"Acción: {action}")
        except Exception as e:
            console.error(f"Error ejecutando acción: {e}")
            console.error(f"Acción: {action}")
    
    def reset_vacuscope_memory(self):
        """
        Resetea la memoria temporal del Vacuoscopio después de usar la información
        """
        self.vacuscope_memory = 0
    
    def _move_in_direction(self, direction: str):
        """
        Mueve el robot en la dirección especificada o ejecuta una rotación
        
        Args:
            direction: Dirección a mover ('front', 'top', 'left', 'right', 'down') 
                      o rotación ('x+90', 'x-90', 'y+90', 'y-90', 'z+90')
        """
        if direction == "front":
            self._move_front()
        elif direction == "top":
            self._move_up()
        elif direction == "left":
            self._move_left()
        elif direction == "right":
            self._move_right()
        elif direction == "down":
            self._move_down()
        elif direction == "x+90":
            self._rotate_x_positive()
        elif direction == "x-90":
            self._rotate_x_negative()
        elif direction == "y+90":
            self._rotate_y_positive()
        elif direction == "y-90":
            self._rotate_y_negative()
        elif direction == "z+90":
            self._move_front()  # z+90 es equivalente a avanzar hacia adelante
        else:
            console.warning(f"Dirección no reconocida: {direction}")
    
    def _move_front(self):
        """Avanza en la dirección actual"""
        x, y, z = self.position
        ox, oy, oz = self.orientation
        
        new_x, new_y, new_z = x + ox, y + oy, z + oz
        
        # Guardar posición anterior antes de moverse
        self.previous_position = tuple(self.position)
        
        if self.environment.is_valid_position(new_x, new_y, new_z):
            old_position = tuple(self.position)
            self.position = [new_x, new_y, new_z]
            new_position = tuple(self.position)
            
            # Actualizar posición en el entorno
            self.environment.update_robot_position(self.id, old_position, new_position)
        else:
            # Colisión con zona vacía o robot - activar memoria del Vacuoscopio
            self.collided_with_empty = True
            self.vacuscope_memory = -1  # Guardar información para la siguiente iteración
            console.warning(f"Robot {self.id_formatted} chocó con zona vacía o robot al frente")
    
    def _move_up(self):
        """Se mueve hacia arriba"""
        x, y, z = self.position
        new_x, new_y, new_z = x, y, z + 1
        
        # Guardar posición anterior antes de moverse
        self.previous_position = tuple(self.position)
        
        if self.environment.is_valid_position(new_x, new_y, new_z):
            old_position = tuple(self.position)
            self.position = [new_x, new_y, new_z]
            new_position = tuple(self.position)
            
            self.environment.update_robot_position(self.id, old_position, new_position)
    
    def _move_left(self):
        """Se mueve a la izquierda"""
        x, y, z = self.position
        ox, oy, oz = self.orientation
        left_orientation = self._rotate_left(ox, oy, oz)
        new_x, new_y, new_z = x + left_orientation[0], y + left_orientation[1], z + left_orientation[2]
        
        # Guardar posición anterior antes de moverse
        self.previous_position = tuple(self.position)
        
        if self.environment.is_valid_position(new_x, new_y, new_z):
            old_position = tuple(self.position)
            self.position = [new_x, new_y, new_z]
            new_position = tuple(self.position)
            
            self.environment.update_robot_position(self.id, old_position, new_position)
    
    def _move_right(self):
        """Se mueve a la derecha"""
        x, y, z = self.position
        ox, oy, oz = self.orientation
        right_orientation = self._rotate_right(ox, oy, oz)
        new_x, new_y, new_z = x + right_orientation[0], y + right_orientation[1], z + right_orientation[2]
        
        # Guardar posición anterior antes de moverse
        self.previous_position = tuple(self.position)
        
        if self.environment.is_valid_position(new_x, new_y, new_z):
            old_position = tuple(self.position)
            self.position = [new_x, new_y, new_z]
            new_position = tuple(self.position)
            
            self.environment.update_robot_position(self.id, old_position, new_position)
    
    def _move_down(self):
        """Se mueve hacia abajo"""
        x, y, z = self.position
        new_x, new_y, new_z = x, y, z - 1
        
        # Guardar posición anterior antes de moverse
        self.previous_position = tuple(self.position)
        
        if self.environment.is_valid_position(new_x, new_y, new_z):
            old_position = tuple(self.position)
            self.position = [new_x, new_y, new_z]
            new_position = tuple(self.position)
            
            self.environment.update_robot_position(self.id, old_position, new_position)
    
    def _rotate_x_positive(self):
        """Rota 90 grados alrededor del eje X (nariz sube)"""
        # Usar el nuevo sistema de rotaciones relativas
        self.orientation = self._calculate_relative_rotation(self.orientation, 'x+90')
        console.info(f"Robot {self.id} rotó X+90° - Nueva orientación: {self.orientation}")
    
    def _rotate_x_negative(self):
        """Rota -90 grados alrededor del eje X (nariz baja)"""
        # Usar el nuevo sistema de rotaciones relativas
        self.orientation = self._calculate_relative_rotation(self.orientation, 'x-90')
        console.info(f"Robot {self.id} rotó X-90° - Nueva orientación: {self.orientation}")
    
    def _rotate_y_positive(self):
        """Rota 90 grados alrededor del eje Y (nariz rota hacia la izquierda)"""
        # Usar el nuevo sistema de rotaciones relativas
        self.orientation = self._calculate_relative_rotation(self.orientation, 'y+90')
        console.info(f"Robot {self.id} rotó Y+90° - Nueva orientación: {self.orientation}")
    
    def _rotate_y_negative(self):
        """Rota -90 grados alrededor del eje Y (nariz rota hacia la derecha)"""
        # Usar el nuevo sistema de rotaciones relativas
        self.orientation = self._calculate_relative_rotation(self.orientation, 'y-90')
        console.info(f"Robot {self.id} rotó Y-90° - Nueva orientación: {self.orientation}")
    
    def _rotate_z_positive(self):
        """Rota 90 grados alrededor del eje Z (rotación en el plano horizontal)"""
        # Rotación alrededor del eje Z: (x, y, z) -> (-y, x, z)
        ox, oy, oz = self.orientation
        self.orientation = [-oy, ox, oz]
        console.info(f"Robot {self.id} rotó Z+90° - Nueva orientación: {self.orientation}")
    
    def _step_back_from_empty(self):
        """
        Retrocede a la posición anterior cuando encuentra zona vacía
        """
        if self.previous_position:
            old_position = tuple(self.position)
            self.position = list(self.previous_position)
            new_position = tuple(self.position)
            
            self.environment.update_robot_position(self.id, old_position, new_position)
            console.info(f"Robot {self.id} retrocedió a posición anterior {new_position}")
            self.collided_with_empty = False
        else:
            console.warning(f"Robot {self.id} no puede retroceder - no hay posición anterior")
    
    def _destroy_monster(self, monsters_list=None, monster_logger=None):
        """Destruye un monstruo en la misma celda donde está el robot"""
        current_position = tuple(self.position)
        
        if self.environment.is_monster_at(current_position):
            # Encontrar y destruir el monstruo en la misma celda
            monster_destroyed = False
            destroyed_monster = None
            if monsters_list:
                for monster in monsters_list:
                    if monster.alive and tuple(monster.position) == current_position:
                        monster.alive = False
                        monster_destroyed = True
                        destroyed_monster = monster
                        self.monsters_destroyed += 1  # Incrementar contador
                        console.success(f"Monstruo {monster.id} destruido en {current_position}")
                        break
            
            # Registrar la muerte del monstruo en el log
            if destroyed_monster and monster_logger:
                operation_data = {
                    'position': list(destroyed_monster.position),
                    'perceptions': {},
                    'rule_number': None,
                    'action': 'death_by_robot',
                    'new_position': list(destroyed_monster.position),
                    'steps_remaining': destroyed_monster.K - destroyed_monster.steps_since_last_action,
                    'K': destroyed_monster.K,
                    'p': destroyed_monster.p,
                    'alive': False
                }
                monster_logger.store_monster_operation(destroyed_monster.id, operation_data)
            
            # Destruir monstruo del registro del environment
            self.environment.remove_monster_at(current_position)
            
            # Generar zona vacía en la posición donde se destruyó el monstruo
            self.environment.create_empty_zone_at(current_position)
            
            # Robot muere también (sacrificio mutuo)
            self.alive = False
            self.environment.unregister_robot(self.id)
            
            # Finalizar log del robot cuando muere
            if self.logger:
                self.logger.finalize_robot_log(self.id)
            
            console.success(f"Robot {self.id} destruyó monstruo en {current_position} y murió")
        else:
            console.warning(f"Robot {self.id} intentó destruir monstruo pero no hay ninguno en {current_position}")
    
    def _save_to_memory(self, perceptions: Dict[str, Any], action: str):
        """
        Guarda la experiencia en la memoria interna
        """
        experience = {
            'step': len(self.memory),
            'perceptions': perceptions.copy(),
            'action': action,
            'position': self.position.copy()
        }
        
        self.memory.append(experience)
        
        # Limitar tamaño de memoria
        if len(self.memory) > self.memory_limit:
            self.memory = self.memory[-self.memory_limit:]
    
    def get_memory_size(self) -> int:
        """
        Obtiene el tamaño de la memoria
        """
        return len(self.memory)
    
    def consult_memory(self, perceptions: Dict[str, Any]) -> Optional[str]:
        """
        Consulta la memoria para ver si hay una acción previa para estas percepciones
        
        Args:
            perceptions: Diccionario con las percepciones actuales
            
        Returns:
            Acción encontrada en memoria o None si no existe
        """
        # Buscar en la memoria una experiencia similar
        for experience in reversed(self.memory):  # Buscar desde la más reciente
            stored_perceptions = experience.get('perceptions', {})
            
            # Comparar percepciones clave (sensores)
            if self._perceptions_match(perceptions, stored_perceptions):
                return experience.get('action')
        
        return None
    
    def _perceptions_match(self, current_perceptions: Dict[str, Any], stored_perceptions: Dict[str, Any]) -> bool:
        """
        Compara si las percepciones actuales coinciden con las almacenadas
        
        Args:
            current_perceptions: Percepciones actuales
            stored_perceptions: Percepciones almacenadas
            
        Returns:
            True si coinciden, False en caso contrario
        """
        # Sensores clave para comparar
        key_sensors = [
            'Energometro', 'Lado1_Top', 'Lado2_Left', 'Vacuoscopio_Front',
            'Lado0_Front', 'Roboscanner_Front', 'Lado3_Right', 'Lado4_Down'
        ]
        
        for sensor in key_sensors:
            if current_perceptions.get(sensor) != stored_perceptions.get(sensor):
                return False
        
        return True
    
    def _determine_executed_direction(self, old_orientation: List[int], new_orientation: List[int]) -> str:
        """
        Determina qué dirección específica se ejecutó basándose en el cambio de orientación
        
        Args:
            old_orientation: Orientación anterior
            new_orientation: Orientación nueva
            
        Returns:
            Dirección específica ejecutada
        """
        # Comparar orientaciones para determinar el movimiento
        if old_orientation != new_orientation:
            # Calcular la diferencia
            diff = [new_orientation[i] - old_orientation[i] for i in range(3)]
            
            # Determinar la dirección basándose en el cambio
            if diff == [1, 0, 0]:  # X+90
                return 'x+90'
            elif diff == [-1, 0, 0]:  # X-90
                return 'x-90'
            elif diff == [0, 1, 0]:  # Y+90
                return 'y+90'
            elif diff == [0, -1, 0]:  # Y-90
                return 'y-90'
            elif diff == [0, 0, 1]:  # Z+90
                return 'z+90'
            elif diff == [0, 0, -1]:  # Z-90
                return 'z-90'
        
        # Si no hay cambio de orientación, fue movimiento hacia adelante
        return 'z+90'
    