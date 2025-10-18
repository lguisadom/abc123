#!/usr/bin/env python3
"""
Módulo RobotLogger - Sistema de logging para operación de robots
Genera archivos CSV con el historial completo de operación de cada robot
"""

import os
import csv
from datetime import datetime
from typing import List, Dict, Any, Tuple
from config import *

class RobotLogger:
    """
    Sistema de logging para robots que genera archivos CSV con la operación completa
    """
    
    def __init__(self):
        """Inicializa el sistema de logging"""
        self.simulation_id = self._generate_simulation_id()
        self.output_dir = self._create_output_directory()
        self.robot_loggers = {}  # {robot_id: RobotOperationLogger}
        
    def _generate_simulation_id(self) -> str:
        """Genera un ID único para la simulación basado en fecha y hora"""
        now = datetime.now()
        return f"simulacion_{now.strftime('%d%m%Y_%H%M%S')}"
    
    def _create_output_directory(self) -> str:
        """Crea la estructura de directorios para la simulación"""
        output_base = "output"
        simulation_dir = os.path.join(output_base, self.simulation_id)
        
        # Crear directorios si no existen
        os.makedirs(simulation_dir, exist_ok=True)
        
        return simulation_dir
    
    def register_robot(self, robot_id: int):
        """Registra un robot para logging"""
        robot_logger = RobotOperationLogger(robot_id, self.output_dir)
        self.robot_loggers[robot_id] = robot_logger
        return robot_logger
    
    def store_robot_operation(self, robot_id: int, operation_data: Dict[str, Any]):
        """Almacena una operación de un robot en memoria (no escribe al CSV aún)"""
        if robot_id in self.robot_loggers:
            self.robot_loggers[robot_id].store_operation(operation_data)
    
    def finalize_robot_log(self, robot_id: int):
        """Finaliza el log de un robot (cuando muere o termina la simulación)"""
        if robot_id in self.robot_loggers:
            self.robot_loggers[robot_id].finalize_log()
    
    def finalize_all_logs(self):
        """Finaliza todos los logs de robots"""
        for robot_logger in self.robot_loggers.values():
            robot_logger.finalize_log()


class RobotOperationLogger:
    """
    Logger individual para un robot específico
    """
    
    def __init__(self, robot_id: int, output_dir: str):
        """
        Inicializa el logger para un robot específico
        
        Args:
            robot_id: ID del robot
            output_dir: Directorio de salida
        """
        self.robot_id = robot_id
        self.output_dir = output_dir
        self.operation_count = 0
        self.csv_file_path = os.path.join(output_dir, f"R{robot_id:03d}.csv")
        self.operations = []  # Almacenar operaciones en memoria
        
        # NO inicializar CSV aún - solo cuando se finalice
    
    def _initialize_csv(self):
        """Inicializa el archivo CSV con los headers"""
        # Headers del CSV según especificación
        headers = [
            '#',                    # Número de operación
            'Pos',                  # Posición del robot
            'Orientacion',          # Orientación del robot
            'Energometro',          # Lectura del energómetro
            'Lado1_Top',           # Monstroscopio lado 1 (Top)
            'Lado2_Left',          # Monstroscopio lado 2 (Left)
            'Vacuoscopio_Front',   # Vacuscopio (Front)
            'Lado0_Front',         # Monstroscopio lado 0 (Front)
            'Roboscanner_Front',   # Roboscanner (Front)
            'Lado3_Right',         # Monstroscopio lado 3 (Right)
            'Lado4_Down',          # Monstroscopio lado 4 (Down)
            'Regla',               # Regla aplicada
            'Nueva_Accion',        # Nueva acción
            'Nueva_Pos'            # Nueva posición
        ]
        
        # Crear archivo CSV
        self.csv_file = open(self.csv_file_path, 'w', newline='', encoding='utf-8')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(headers)
    
    def store_operation(self, operation_data: Dict[str, Any]):
        """
        Almacena una operación del robot en memoria (no escribe al CSV aún)
        
        Args:
            operation_data: Diccionario con todos los datos de la operación
        """
        self.operation_count += 1
        
        # Agregar número de operación a los datos
        operation_data['operation_number'] = self.operation_count
        
        # Almacenar en memoria
        self.operations.append(operation_data)
    
    def finalize_log(self):
        """Finaliza el log escribiendo todas las operaciones almacenadas al CSV"""
        if not self.operations:
            return  # No hay operaciones para escribir
        
        # Inicializar CSV ahora
        self._initialize_csv()
        
        # Escribir todas las operaciones almacenadas
        for operation_data in self.operations:
            self._write_operation_to_csv(operation_data)
        
        # Cerrar archivo
        if self.csv_file:
            self.csv_file.close()
            self.csv_file = None
            self.csv_writer = None
    
    def _write_operation_to_csv(self, operation_data: Dict[str, Any]):
        """Escribe una operación al CSV"""
        if not self.csv_writer:
            return
        
        # Extraer datos de la operación
        position = operation_data.get('position', (0, 0, 0))
        orientation = operation_data.get('orientation', [0, 0, 1])
        sensors = operation_data.get('sensors', {})
        rule_num = operation_data.get('rule_num', 0)
        action = operation_data.get('action', '')
        new_position = operation_data.get('new_position', position)
        operation_number = operation_data.get('operation_number', 0)
        
        # Formatear datos para CSV
        row = [
            operation_number,                                        # #
            f"[{position[0]},{position[1]},{position[2]}]",        # Pos
            f"[{orientation[0]},{orientation[1]},{orientation[2]}]", # Orientacion
            sensors.get('Energometro', 0),                          # Energometro
            sensors.get('Lado1_Top', 0),                            # Lado1_Top
            sensors.get('Lado2_Left', 0),                           # Lado2_Left
            sensors.get('Vacuoscopio_Front', 0),                     # Vacuoscopio_Front
            sensors.get('Lado0_Front', 0),                          # Lado0_Front
            sensors.get('Roboscanner_Front', 0),                    # Roboscanner_Front
            sensors.get('Lado3_Right', 0),                          # Lado3_Right
            sensors.get('Lado4_Down', 0),                           # Lado4_Down
            rule_num,                                               # Regla
            action,                                                 # Nueva_Accion
            f"[{new_position[0]},{new_position[1]},{new_position[2]}]" # Nueva_Pos
        ]
        
        # Escribir fila en CSV
        self.csv_writer.writerow(row)
        self.csv_file.flush()  # Asegurar que se escriba inmediatamente
