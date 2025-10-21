#!/usr/bin/env python3
"""
Módulo MonsterLogger - Sistema de logging para operación de monstruos
Genera archivos CSV con el historial completo de operación de cada monstruo
"""

import os
import csv
import json
from datetime import datetime
from typing import List, Dict, Any, Tuple
from config import *

class MonsterLogger:
    """
    Sistema de logging para monstruos que genera archivos CSV con la operación completa
    """
    
    def __init__(self):
        """Inicializa el sistema de logging"""
        self.simulation_id = self._generate_simulation_id()
        self.output_dir = self._create_output_directory()
        self.monster_loggers = {}  # {monster_id: MonsterOperationLogger}
        
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
    
    def register_monster(self, monster_id: int):
        """Registra un monstruo para logging"""
        monster_logger = MonsterOperationLogger(monster_id, self.output_dir)
        self.monster_loggers[monster_id] = monster_logger
        return monster_logger
    
    def store_monster_operation(self, monster_id: int, operation_data: Dict[str, Any]):
        """Almacena una operación de un monstruo en memoria (no escribe al CSV aún)"""
        if monster_id in self.monster_loggers:
            self.monster_loggers[monster_id].store_operation(operation_data)
    
    def finalize_all_logs(self, simulation_stats: Dict[str, Any] = None):
        """Finaliza todos los logs y genera los archivos CSV"""
        for monster_logger in self.monster_loggers.values():
            monster_logger.finalize_log()
        
        # No generar estadísticas finales aquí - el RobotLogger se encarga
        print(f"📁 Logs de monstruos finalizados en: {self.output_dir}")

class MonsterOperationLogger:
    """
    Logger individual para un monstruo específico
    """
    
    def __init__(self, monster_id: int, output_dir: str):
        """
        Inicializa el logger para un monstruo específico
        
        Args:
            monster_id: ID del monstruo
            output_dir: Directorio de salida
        """
        self.monster_id = monster_id
        self.monster_id_formatted = f"M{monster_id:03d}"
        self.output_dir = output_dir
        self.operations = []  # Lista de operaciones en memoria
        self.csv_file = None
        self.csv_writer = None
        
    def store_operation(self, operation_data: Dict[str, Any]):
        """
        Almacena una operación en memoria
        
        Args:
            operation_data: Diccionario con los datos de la operación
        """
        # Agregar datos adicionales
        operation_data['monster_id'] = self.monster_id
        operation_data['monster_id_formatted'] = self.monster_id_formatted
        
        self.operations.append(operation_data)
    
    def finalize_log(self):
        """Finaliza el log y genera el archivo CSV"""
        if not self.operations:
            return
        
        # Crear archivo CSV
        csv_filename = f"{self.monster_id_formatted}.csv"
        csv_path = os.path.join(self.output_dir, csv_filename)
        
        # Definir columnas del CSV
        fieldnames = [
            '#', 'Pos', 'Top', 'Left', 'Front', 'Right', 'Down', 'Behind', 
            'n_free', 'p', 'Regla', 'Accion', 'Steps_Remaining', 'K', 'Alive'
        ]
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for i, operation in enumerate(self.operations, 1):
                # Preparar datos para CSV
                csv_data = {
                    '#': i,
                    'Pos': operation.get('position', ''),
                    'Top': operation.get('perceptions', {}).get('Top', ''),
                    'Left': operation.get('perceptions', {}).get('Left', ''),
                    'Front': operation.get('perceptions', {}).get('Front', ''),
                    'Right': operation.get('perceptions', {}).get('Right', ''),
                    'Down': operation.get('perceptions', {}).get('Down', ''),
                    'Behind': operation.get('perceptions', {}).get('Behind', ''),
                    'n_free': operation.get('perceptions', {}).get('n_free', ''),
                    'p': operation.get('p', ''),
                    'Regla': operation.get('rule_number', ''),
                    'Accion': operation.get('action', ''),
                    'Steps_Remaining': operation.get('steps_remaining', ''),
                    'K': operation.get('K', ''),
                    'Alive': operation.get('alive', True)
                }
                
                writer.writerow(csv_data)
        
        print(f"📁 Log del monstruo {self.monster_id_formatted} guardado en: {csv_path}")
