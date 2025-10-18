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
        
        # Resetear memoria del Vacuoscopio después de usarla
        if resetVacuscopeMemory == True and self.vacuscope_memory == -1:
            self.reset_vacuscope_memory()
        
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
        
        # Usar motor de reglas si está disponible
        if self.rule_engine:
            action = self.rule_engine.get_robot_action(perceptions)
            rule_num = self.rule_engine.get_robot_rule_number(perceptions)
        else:
            # Comportamiento por defecto si no hay motor de reglas
            action = self._default_behavior(perceptions)
            rule_num = 0
        
        # Calcular nueva posición y orientación después de la acción
        new_position, new_orientation = self._calculate_new_state(action)
        
        # Guardar datos para logging (solo almacenar, no escribir aún)
        if self.logger:
            operation_data = {
                'position': initial_position,
                'orientation': initial_orientation,
                'sensors': perceptions,
                'rule_num': rule_num,
                'action': action,
                'new_position': new_position,
                'new_orientation': new_orientation
            }
            self.logger.store_robot_operation(self.id, operation_data)
        
        # Guardar en memoria
        self._save_to_memory(perceptions, action)
        
        self.steps_since_last_action = 0
        
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
    
    def _calculate_new_state(self, action: str) -> Tuple[Tuple[int, int, int], List[int]]:
        """
        Calcula la nueva posición y orientación que tendría el robot después de ejecutar la acción
        Sin ejecutar realmente la acción
        
        Args:
            action: Acción a simular
            
        Returns:
            Tuple con (nueva_posición, nueva_orientación)
        """
        try:
            action_data = json.loads(action)
            action_type = action_data.get('tipo')
            
            new_position = tuple(self.position)
            new_orientation = self.orientation.copy()
            
            if action_type == 'destroy':
                # La posición y orientación no cambian al destruir
                pass
            elif action_type == 'memory':
                # Retroceder de zona vacía - simular movimiento hacia atrás
                new_position = self._get_backward_position(*self.position)
            elif action_type == 'idle':
                # No cambiar posición ni orientación
                pass
            elif action_type == 'move':
                directions = action_data.get('directions', [])
                if directions:
                    direction = directions[0]
                    if direction == 'front':
                        candidate_position = self._get_front_position(*self.position)
                        new_position = candidate_position if self.environment.is_valid_position(*candidate_position) else tuple(self.position)
                    elif direction == 'back':
                        candidate_position = self._get_backward_position(*self.position)
                        new_position = candidate_position if self.environment.is_valid_position(*candidate_position) else tuple(self.position)
                    elif direction == 'left':
                        candidate_position = self._get_left_position(*self.position)
                        new_position = candidate_position if self.environment.is_valid_position(*candidate_position) else tuple(self.position)
                    elif direction == 'right':
                        candidate_position = self._get_right_position(*self.position)
                        new_position = candidate_position if self.environment.is_valid_position(*candidate_position) else tuple(self.position)
                    elif direction == 'up':
                        candidate_position = self._get_up_position(*self.position)
                        new_position = candidate_position if self.environment.is_valid_position(*candidate_position) else tuple(self.position)
                    elif direction == 'down':
                        candidate_position = self._get_down_position(*self.position)
                        new_position = candidate_position if self.environment.is_valid_position(*candidate_position) else tuple(self.position)
                    elif direction == 'z+90':
                        new_position = self._calculate_z_forward_position()
            elif action_type == 'move_random':
                directions = action_data.get('directions', [])
                if directions:
                    # Para simulación, usar la primera dirección
                    direction = directions[0]
                    if direction == 'front':
                        candidate_position = self._get_front_position(*self.position)
                        new_position = candidate_position if self.environment.is_valid_position(*candidate_position) else tuple(self.position)
                    elif direction == 'back':
                        candidate_position = self._get_backward_position(*self.position)
                        new_position = candidate_position if self.environment.is_valid_position(*candidate_position) else tuple(self.position)
                    elif direction == 'left':
                        candidate_position = self._get_left_position(*self.position)
                        new_position = candidate_position if self.environment.is_valid_position(*candidate_position) else tuple(self.position)
                    elif direction == 'right':
                        candidate_position = self._get_right_position(*self.position)
                        new_position = candidate_position if self.environment.is_valid_position(*candidate_position) else tuple(self.position)
                    elif direction == 'up':
                        candidate_position = self._get_up_position(*self.position)
                        new_position = candidate_position if self.environment.is_valid_position(*candidate_position) else tuple(self.position)
                    elif direction == 'down':
                        candidate_position = self._get_down_position(*self.position)
                        new_position = candidate_position if self.environment.is_valid_position(*candidate_position) else tuple(self.position)
            elif action_type == 'rotate':
                directions = action_data.get('directions', [])
                if directions:
                    direction = directions[0]
                    if direction == 'left':
                        new_orientation = self._rotate_left(*self.orientation)
                    elif direction == 'right':
                        new_orientation = self._rotate_right(*self.orientation)
                    elif direction == 'x+90':
                        new_orientation = self._rotate_x_plus_90(*self.orientation)
                    elif direction == 'x-90':
                        new_orientation = self._rotate_x_minus_90(*self.orientation)
                    elif direction == 'y+90':
                        new_orientation = self._rotate_y_plus_90(*self.orientation)
                    elif direction == 'y-90':
                        new_orientation = self._rotate_y_minus_90(*self.orientation)
            
            return new_position, new_orientation
            
        except (json.JSONDecodeError, KeyError, IndexError):
            # Si hay error en la acción, no cambiar estado
            return tuple(self.position), self.orientation.copy()
    
    def execute_action(self, action: str, monsters_list=None):
        """
        Ejecuta la acción especificada
        
        Args:
            action: Acción a ejecutar
            monsters_list: Lista de monstruos para acciones de destrucción
        """
        self._execute_action(action, monsters_list)
    
    def _default_behavior(self, perceptions: Dict[str, Any]) -> str:
        """
        Comportamiento por defecto cuando no hay motor de reglas
        """
        # Comportamiento simple por defecto
        if perceptions.get('Lado0_Front', 0) == 1:
            return '{"tipo": "move", "directions": ["front"]}'
        elif perceptions.get('Vacuoscopio_Front', 0) == -1:
            return '{"tipo": "memory", "notes": "avoid_previous_empty"}'
        else:
            return '{"tipo": "move", "directions": ["front"]}'
    
    def _execute_action(self, action: str, monsters_list=None):
        """
        Ejecuta la acción especificada según el formato JSON
        """
        try:
            # Parsear la acción JSON
            action_data = json.loads(action)
            action_type = action_data.get('tipo')
            
            if action_type == 'destroy':
                self._destroy_monster(monsters_list)
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
                    chosen_direction = random.choice(directions)
                    self._move_in_direction(chosen_direction)
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
        # Rotación alrededor del eje X: (x, y, z) -> (x, -z, y)
        ox, oy, oz = self.orientation
        self.orientation = [ox, -oz, oy]
        console.info(f"Robot {self.id} rotó X+90° - Nueva orientación: {self.orientation}")
    
    def _rotate_x_negative(self):
        """Rota -90 grados alrededor del eje X (nariz baja)"""
        # Rotación alrededor del eje X: (x, y, z) -> (x, z, -y)
        ox, oy, oz = self.orientation
        self.orientation = [ox, oz, -oy]
        console.info(f"Robot {self.id} rotó X-90° - Nueva orientación: {self.orientation}")
    
    def _rotate_y_positive(self):
        """Rota 90 grados alrededor del eje Y (nariz rota hacia la izquierda)"""
        # Rotación alrededor del eje Y: (x, y, z) -> (z, y, -x)
        ox, oy, oz = self.orientation
        self.orientation = [oz, oy, -ox]
        console.info(f"Robot {self.id} rotó Y+90° - Nueva orientación: {self.orientation}")
    
    def _rotate_y_negative(self):
        """Rota -90 grados alrededor del eje Y (nariz rota hacia la derecha)"""
        # Rotación alrededor del eje Y: (x, y, z) -> (-z, y, x)
        ox, oy, oz = self.orientation
        self.orientation = [-oz, oy, ox]
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
    
    def _destroy_monster(self, monsters_list=None):
        """Destruye un monstruo en la misma celda donde está el robot"""
        current_position = tuple(self.position)
        
        if self.environment.is_monster_at(current_position):
            # Encontrar y destruir el monstruo en la misma celda
            monster_destroyed = False
            if monsters_list:
                for monster in monsters_list:
                    if monster.alive and tuple(monster.position) == current_position:
                        monster.alive = False
                        monster_destroyed = True
                        self.monsters_destroyed += 1  # Incrementar contador
                        console.success(f"Monstruo {monster.id} destruido en {current_position}")
                        break
            
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
    