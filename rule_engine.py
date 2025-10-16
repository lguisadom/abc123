import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import os

class RuleEngine:
    """
    Motor de reglas para cargar y aplicar tablas de percepción-acción desde archivos CSV
    """
    
    def __init__(self, robot_rules_file: str = "data/robot_rules.csv", 
                 monster_rules_file: str = "data/monster_rules.csv"):
        """
        Inicializa el motor de reglas
        
        Args:
            robot_rules_file: Ruta al archivo CSV con reglas de robots
            monster_rules_file: Ruta al archivo CSV con reglas de monstruos
        """
        self.robot_rules_file = robot_rules_file
        self.monster_rules_file = monster_rules_file
        
        # DataFrames para almacenar las reglas
        self.robot_rules = None
        self.monster_rules = None
        
        # Cargar reglas al inicializar
        self.load_rules()
    
    def load_rules(self) -> bool:
        """
        Carga las reglas desde los archivos CSV
        
        Returns:
            bool: True si se cargaron correctamente, False en caso contrario
        """
        try:
            # Cargar reglas de robots
            if os.path.exists(self.robot_rules_file):
                self.robot_rules = pd.read_csv(self.robot_rules_file)
                print(f"✅ Reglas de robots cargadas: {len(self.robot_rules)} reglas")
            else:
                print(f"⚠️ Archivo de reglas de robots no encontrado: {self.robot_rules_file}")
                return False
            
            # Cargar reglas de monstruos
            if os.path.exists(self.monster_rules_file):
                self.monster_rules = pd.read_csv(self.monster_rules_file)
                print(f"✅ Reglas de monstruos cargadas: {len(self.monster_rules)} reglas")
            else:
                print(f"⚠️ Archivo de reglas de monstruos no encontrado: {self.monster_rules_file}")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error cargando reglas: {e}")
            return False
    
    
    def get_robot_action(self, perception: Dict[str, any]) -> Optional[str]:
        """
        Obtiene la acción para un robot basada en su percepción
        
        Args:
            perception: Diccionario con los valores de los sensores del robot
            
        Returns:
            str: Acción a ejecutar, o None si no se encuentra regla coincidente
        """
        if self.robot_rules is None:
            return None
        
        try:
            # Buscar regla que coincida con la percepción
            for _, rule in self.robot_rules.iterrows():
                if self._matches_robot_perception(rule, perception):
                    return rule['Accion']
            
            # Si no se encuentra regla específica, usar acción por defecto
            return '{"tipo": "move", "directions": ["front"]}'
            
        except Exception as e:
            print(f"❌ Error obteniendo acción de robot: {e}")
            return '{"tipo": "move", "directions": ["front"]}'
    
    def get_monster_action(self, perception: Dict[str, any]) -> Optional[str]:
        """
        Obtiene la acción para un monstruo basada en su percepción
        
        Args:
            perception: Diccionario con los valores de percepción del monstruo
                       Formato: {Top, Left, Front, Right, Down, Behind}
            
        Returns:
            str: Acción a ejecutar, o None si no se encuentra regla coincidente
        """
        if self.monster_rules is None:
            return None
        
        try:
            # Buscar regla que coincida con la percepción
            for _, rule in self.monster_rules.iterrows():
                if self._matches_monster_perception(rule, perception):
                    return rule['Accion']
            
            # Si no se encuentra regla específica, usar acción por defecto
            return "wait"
            
        except Exception as e:
            print(f"❌ Error obteniendo acción de monstruo: {e}")
            return "wait"
    
    
    def _matches_monster_perception(self, rule: pd.Series, perception: Dict[str, any]) -> bool:
        """
        Verifica si una regla de monstruo coincide con la percepción actual
        
        Args:
            rule: Fila de regla del DataFrame
            perception: Diccionario con la percepción actual
                       Formato: {Top, Left, Front, Right, Down, Behind}
            
        Returns:
            bool: True si la regla coincide
        """
        try:
            # Direcciones en el orden del CSV
            directions = ['Top', 'Left', 'Front', 'Right', 'Down', 'Behind']
            
            # Comparar cada dirección
            for direction in directions:
                if direction in rule.index and direction in perception:
                    rule_value = rule[direction]
                    perception_value = perception[direction]
                    
                    # Comparar valores
                    if rule_value != perception_value:
                        return False
                else:
                    # Si falta alguna dirección, no coincide
                    return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error comparando percepción de monstruo: {e}")
            return False
    
    def _matches_robot_perception(self, rule: pd.Series, perception: Dict[str, any]) -> bool:
        """
        Verifica si una regla de robot coincide con la percepción actual
        CASO ESPECIAL: Si Energometro = 1 en la regla, solo comparar Energometro
        """
        try:
            # Columnas de percepción del robot según la imagen (orden correcto)
            perception_columns = [
                'Energometro', 'Lado1_Top', 'Lado2_Left', 'Vacuoscopio_Front', 
                'Lado0_Front', 'Roboscanner_Front', 'Lado3_Right', 'Lado4_Down'
            ]
            
            # CASO ESPECIAL: Si Energometro = 1 en la regla, solo comparar Energometro
            rule_energometro = int(rule['Energometro']) if rule['Energometro'] is not None else 0
            perception_energometro = int(perception.get('Energometro', 0)) if perception.get('Energometro', 0) is not None else 0
            
            if rule_energometro == 1:
                # Solo verificar que el Energometro coincida
                match = perception_energometro == 1
                if match:
                    rule_num = rule.get('Regla', 'N/A')
                return match
            
            # Para el resto de reglas, verificar todos los sensores
            for column in perception_columns:
                if column in rule.index and column in perception:
                    rule_value = rule[column]
                    perception_value = perception[column]
                    
                    # Comparar valores
                    if rule_value != perception_value:
                        return False
                else:
                    # Si falta alguna columna, no coincide
                    return False
            
            # Solo mostrar cuando coincide completamente
            rule_num = rule.get('Regla', 'N/A')
            return True
            
        except Exception as e:
            print(f"❌ Error comparando percepción de robot: {e}")
            return False
    
    
    def print_rules_summary(self):
        """
        Imprime un resumen de las reglas cargadas
        """
        print("\n📋 Resumen de Reglas Cargadas:")
        print("=" * 50)
        
        if self.robot_rules is not None:
            print(f"🤖 Reglas de Robots: {len(self.robot_rules)} reglas")
            print(f"   Columnas: {list(self.robot_rules.columns)}")
            print(f"   Acciones disponibles: {self.robot_rules['Accion'].unique()}")
        
        if self.monster_rules is not None:
            print(f"👹 Reglas de Monstruos: {len(self.monster_rules)} reglas")
            print(f"   Columnas: {list(self.monster_rules.columns)}")
            print(f"   Acciones disponibles: {self.monster_rules['Accion'].unique()}")
        
        print("=" * 50)
    
    def validate_rules(self) -> Dict[str, List[str]]:
        """
        Valida la estructura de las reglas cargadas
        
        Returns:
            Dict con errores encontrados por tipo de agente
        """
        errors = {'robot': [], 'monster': []}
        
        # Validar reglas de robots
        if self.robot_rules is not None:
            if 'Accion' not in self.robot_rules.columns:
                errors['robot'].append("Falta columna 'Accion'")
            
            # Verificar que todas las acciones sean válidas
            # Las acciones de robots ahora son strings complejos según la imagen
            pass
        
        # Validar reglas de monstruos
        if self.monster_rules is not None:
            if 'Accion' not in self.monster_rules.columns:
                errors['monster'].append("Falta columna 'Accion'")
            
            # Verificar que todas las acciones sean válidas
            # Las acciones de monstruos pueden ser probabilísticas o determinísticas
            # No validamos acciones específicas ya que son strings complejos
            pass
        
        return errors
    
    def get_robot_rule_number(self, perceptions: Dict[str, Any]) -> Optional[int]:
        """
        Obtiene el número de regla que coincide con las percepciones del robot
        
        Args:
            perceptions: Diccionario con las percepciones del robot
            
        Returns:
            Número de regla que coincide o None si no hay coincidencia
        """
        if self.robot_rules is None:
            return None
        
        # Buscar la regla que coincide
        for index, row in self.robot_rules.iterrows():
            if self._matches_robot_perception(row, perceptions):
                # Retornar el número de regla (índice + 1 para que empiece en 1)
                return index + 1
        
        return None
