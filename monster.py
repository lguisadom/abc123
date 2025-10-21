import random
from typing import List, Dict, Any, Optional
from config import MONSTER_FREQUENCY, MONSTER_PROBABILITY
from console_formatter import console

class Monster:
    """
    Clase que representa un monstruo en el entorno 3D
    
    Los monstruos son entidades energéticas que actúan como agentes reflejo simples.
    No tienen orientación propia y se mueven según coordenadas globales absolutas.
    Su comportamiento está completamente definido por el archivo monster_rules.csv
    """
    
    def __init__(self, monster_id: int, position: List[int], environment, rule_engine, logger=None):
        """
        Inicializa un monstruo
        
        Args:
            monster_id: Identificador único del monstruo
            position: Posición inicial (x, y, z)
            environment: Referencia al entorno
            rule_engine: Motor de reglas para comportamiento
            logger: Sistema de logging para operaciones
        """
        self.id = monster_id
        self.id_formatted = f"M{monster_id:03d}"  # Formato M001, M002, etc.
        self.position = list(position)  # Convertir a lista para mutabilidad
        self.environment = environment
        self.rule_engine = rule_engine
        self.logger = logger
        
        # Estado del monstruo
        self.alive = True
        
        # Parámetros de comportamiento (K y p)
        self.K = MONSTER_FREQUENCY  # Cada cuántas iteraciones puede actuar
        self.p = MONSTER_PROBABILITY  # Probabilidad de moverse en cada turno
        
        # Control de turnos
        self.steps_since_last_action = 0
        self.last_action = None
        
        # Registrar monstruo en el entorno
        self.environment.register_monster(self.id, tuple(self.position))
    
    def perceive(self) -> Dict[str, Any]:
        """
        Realiza la percepción del entorno usando coordenadas globales absolutas
        
        Returns:
            Dict con las percepciones en formato: {Top, Left, Front, Right, Down, Behind}
        """
        x, y, z = self.position
        
        # Definir las 6 direcciones globales absolutas
        directions = {
            'Top': (x, y, z + 1),      # Arriba (Z+)
            'Left': (x - 1, y, z),     # Izquierda (X-)
            'Front': (x, y + 1, z),    # Frente (Y+)
            'Right': (x + 1, y, z),    # Derecha (X+)
            'Down': (x, y, z - 1),     # Abajo (Z-)
            'Behind': (x, y - 1, z)     # Atrás (Y-)
        }
        
        perceptions = {}
        
        # Evaluar cada dirección
        for direction, (nx, ny, nz) in directions.items():
            if self.environment.is_valid_position(nx, ny, nz):
                perceptions[direction] = 0  # Zona libre
            else:
                perceptions[direction] = -1  # Zona vacía
        
        return perceptions
    
    def act(self, perceptions: Dict[str, Any]) -> str:
        """
        Decide y ejecuta una acción basada en las percepciones usando el motor de reglas
        
        Args:
            perceptions: Diccionario con las percepciones en formato global
            
        Returns:
            str: Acción ejecutada
        """
        if not self.alive:
            # Log para monstruo muerto
            if self.logger:
                operation_data = {
                    'position': list(self.position),
                    'perceptions': perceptions,
                    'rule_number': None,
                    'action': 'none',
                    'new_position': list(self.position),
                    'steps_remaining': self.K - self.steps_since_last_action,
                    'K': self.K,
                    'p': self.p,
                    'alive': False
                }
                self.logger.store_monster_operation(self.id, operation_data)
            return "none"
        
        # Calcular pasos restantes
        steps_remaining = self.K - self.steps_since_last_action
        
        # Verificar si puede actuar según parámetro K
        self.steps_since_last_action += 1
        if self.steps_since_last_action < self.K:
            # Log para espera por K
            if self.logger:
                operation_data = {
                    'position': list(self.position),
                    'perceptions': perceptions,
                    'rule_number': None,
                    'action': 'wait',
                    'new_position': list(self.position),
                    'steps_remaining': steps_remaining - 1,
                    'K': self.K,
                    'p': self.p,
                    'alive': True
                }
                self.logger.store_monster_operation(self.id, operation_data)
            return "wait"
        
        # Verificar probabilidad p
        if random.random() > self.p:
            self.steps_since_last_action = 0  # Resetear contador
            # Log para espera por probabilidad
            if self.logger:
                operation_data = {
                    'position': list(self.position),
                    'perceptions': perceptions,
                    'rule_number': None,
                    'action': 'wait',
                    'new_position': list(self.position),
                    'steps_remaining': self.K,
                    'K': self.K,
                    'p': self.p,
                    'alive': True
                }
                self.logger.store_monster_operation(self.id, operation_data)
            return "wait"
        
        # Usar motor de reglas si está disponible
        if self.rule_engine:
            action = self.rule_engine.get_monster_action(perceptions)
            rule_number = self.rule_engine.get_monster_rule_number(perceptions)
        else:
            # Comportamiento por defecto si no hay motor de reglas
            action = self._default_behavior(perceptions)
            rule_number = None
        
        # Guardar posición anterior
        old_position = list(self.position)
        
        # Ejecutar la acción
        self._execute_action(action)
        
        # Log para acción ejecutada
        if self.logger:
            operation_data = {
                'position': old_position,
                'perceptions': perceptions,
                'rule_number': rule_number,
                'action': action,
                'new_position': list(self.position),
                'steps_remaining': self.K,
                'K': self.K,
                'p': self.p,
                'alive': True
            }
            self.logger.store_monster_operation(self.id, operation_data)
        
        # Resetear contador de pasos
        self.steps_since_last_action = 0
        self.last_action = action
        
        return action
    
    def _default_behavior(self, perceptions: Dict[str, Any]) -> str:
        """
        Comportamiento por defecto cuando no hay motor de reglas
        
        Args:
            perceptions: Diccionario con las percepciones
            
        Returns:
            str: Acción a ejecutar
        """
        # Buscar una dirección libre
        free_directions = [d for d, v in perceptions.items() if v == 0]
        if free_directions:
            return f"move_{random.choice(free_directions).lower()}"
        else:
            return "wait"  # No puede moverse
    
    def _execute_action(self, action: str):
        """
        Ejecuta la acción especificada
        
        Args:
            action: Acción a ejecutar (puede ser probabilística o determinística)
        """
        if action == "wait":
            pass  # No hacer nada
        elif action.startswith("Mover aleatorio entre"):
            # Acción probabilística: extraer direcciones disponibles
            self._execute_probabilistic_action(action)
        elif action.startswith("Mover hacia"):
            # Acción determinística: mover en dirección específica
            self._execute_deterministic_action(action)
        # Si la acción no es reconocida, no hacer nada
    
    def _execute_probabilistic_action(self, action: str):
        """
        Ejecuta una acción probabilística
        
        Args:
            action: String con formato "Mover aleatorio entre [dir1, dir2, ...]"
        """
        try:
            # Extraer las direcciones del string
            # Formato: "Mover aleatorio entre [Top, Left, Front, Right, Down, Behind]"
            start = action.find('[') + 1
            end = action.find(']')
            directions_str = action[start:end]
            
            # Parsear direcciones
            directions = [d.strip() for d in directions_str.split(',')]
            
            # Elegir dirección aleatoria
            if directions:
                chosen_direction = random.choice(directions)
                self._move_to_direction(chosen_direction)
                
        except Exception as e:
            console.error(f"Error ejecutando acción probabilística: {e}")
    
    def _execute_deterministic_action(self, action: str):
        """
        Ejecuta una acción determinística
        
        Args:
            action: String con formato "Mover hacia [dirección]"
        """
        try:
            # Extraer la dirección del string
            # Formato: "Mover hacia [Behind]"
            start = action.find('[') + 1
            end = action.find(']')
            direction = action[start:end].strip()
            
            # Mover en la dirección especificada
            self._move_to_direction(direction)
            
        except Exception as e:
            console.error(f"Error ejecutando acción determinística: {e}")
    
    def _move_to_direction(self, direction: str):
        """
        Mueve el monstruo en la dirección especificada
        
        Args:
            direction: Dirección a moverse (Top, Left, Front, Right, Down, Behind)
        """
        x, y, z = self.position
        
        # Mapear direcciones a coordenadas
        direction_map = {
            'Top': (x, y, z + 1),
            'Left': (x - 1, y, z),
            'Front': (x, y + 1, z),
            'Right': (x + 1, y, z),
            'Down': (x, y, z - 1),
            'Behind': (x, y - 1, z)
        }
        
        if direction in direction_map:
            new_x, new_y, new_z = direction_map[direction]
            
            if self.environment.is_valid_position(new_x, new_y, new_z):
                old_position = tuple(self.position)
                self.position = [new_x, new_y, new_z]
                new_position = tuple(self.position)
                
                # Actualizar posición en el entorno
                self.environment.update_monster_position(self.id, old_position, new_position)
    
