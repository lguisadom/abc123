#!/usr/bin/env python3
"""
Módulo RobotLogger - Sistema de logging para operación de robots
Genera archivos CSV con el historial completo de operación de cada robot
"""

import os
import csv
import json
from datetime import datetime
from typing import List, Dict, Any, Tuple
from config import *

class RobotLogger:
    """
    Sistema de logging para robots que genera archivos CSV con la operación completa
    """
    
    def __init__(self, monster_logger=None):
        """Inicializa el sistema de logging"""
        self.simulation_id = self._generate_simulation_id()
        self.output_dir = self._create_output_directory()
        self.robot_loggers = {}  # {robot_id: RobotOperationLogger}
        self.monster_logger = monster_logger  # Referencia al logger de monstruos
        
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
    
    def finalize_all_logs(self, simulation_stats: Dict[str, Any] = None):
        """Finaliza todos los logs de robots y genera estadísticas finales"""
        for robot_logger in self.robot_loggers.values():
            robot_logger.finalize_log()
        
        # Generar estadísticas finales si se proporcionan
        if simulation_stats:
            self._generate_final_stats(simulation_stats)
    
    def _generate_final_stats(self, simulation_stats: Dict[str, Any]):
        """
        Genera un archivo de estadísticas finales de la simulación
        
        Args:
            simulation_stats: Diccionario con estadísticas de la simulación
        """
        stats_file_path = os.path.join(self.output_dir, "estadisticas_finales.json")
        
        # Preparar estadísticas con información adicional
        final_stats = {
            "simulacion": {
                "id": self.simulation_id,
                "fecha_inicio": simulation_stats.get("fecha_inicio", datetime.now().isoformat()),
                "fecha_fin": datetime.now().isoformat(),
                "duracion_segundos": simulation_stats.get("duracion_segundos", 0),
                "pasos_ejecutados": simulation_stats.get("pasos_ejecutados", 0),
                "configuracion": {
                    "tamaño_mundo": WORLD_SIZE,
                    "num_robots": NUM_ROBOTS,
                    "num_monstruos": NUM_MONSTERS,
                    "pasos_simulacion": SIMULATION_STEPS,
                    "frecuencia_robot": ROBOT_FREQUENCY,
                    "frecuencia_monstruo": MONSTER_FREQUENCY,
                    "probabilidad_monstruo": MONSTER_PROBABILITY,
                    "limite_memoria_robot": ROBOT_MEMORY_LIMIT
                }
            },
            "resultados": {
                "robots_vivos": simulation_stats.get("robots_vivos", 0),
                "robots_muertos": simulation_stats.get("robots_muertos", 0),
                "monstruos_vivos": simulation_stats.get("monstruos_vivos", 0),
                "monstruos_eliminados": simulation_stats.get("monstruos_eliminados", 0),
                "robots_eliminados": simulation_stats.get("robots_eliminados", 0)
            },
            "estadisticas_robots": self._calculate_robot_stats(),
            "estadisticas_monstruos": self._calculate_monster_stats(),
            "estadisticas_entorno": {
                "zonas_libres": simulation_stats.get("zonas_libres", 0),
                "zonas_vacias": simulation_stats.get("zonas_vacias", 0),
                "porcentaje_cobertura": simulation_stats.get("porcentaje_cobertura", 0)
            }
        }
        
        # Guardar estadísticas en archivo JSON
        try:
            with open(stats_file_path, 'w', encoding='utf-8') as f:
                json.dump(final_stats, f, indent=2, ensure_ascii=False)
            print(f"✅ Estadísticas finales guardadas en: {stats_file_path}")
        except Exception as e:
            print(f"❌ Error guardando estadísticas finales: {e}")
    
    def _calculate_monster_stats(self) -> Dict[str, Any]:
        """
        Calcula estadísticas de todos los monstruos
        
        Returns:
            Diccionario con estadísticas de monstruos
        """
        monster_stats = {}
        
        if not self.monster_logger:
            return monster_stats
        
        for monster_id, monster_logger in self.monster_logger.monster_loggers.items():
            operations = monster_logger.operations
            
            if not operations:
                continue
            
            # Calcular estadísticas del monstruo
            total_operations = len(operations)
            rules_used = {}
            wait_actions = 0
            move_actions = 0
            
            for op in operations:
                rule_num = op.get('rule_number')
                if rule_num is not None:
                    rules_used[rule_num] = rules_used.get(rule_num, 0) + 1
                
                action = op.get('action', '')
                if action == 'wait':
                    wait_actions += 1
                elif action.startswith('move_'):
                    move_actions += 1
            
            # Calcular porcentajes
            wait_percentage = (wait_actions / total_operations * 100) if total_operations > 0 else 0
            move_percentage = (move_actions / total_operations * 100) if total_operations > 0 else 0
            
            # Obtener posición y estado final
            final_position = operations[-1].get('new_position', [0, 0, 0]) if operations else [0, 0, 0]
            alive = operations[-1].get('alive', True) if operations else True
            
            # Obtener parámetros K y p
            K = operations[-1].get('K', 10) if operations else 10
            p = operations[-1].get('p', 0.1) if operations else 0.1
            
            monster_stats[f"monster_{monster_id:03d}"] = {
                "total_operaciones": total_operations,
                "acciones_espera": {
                    "veces_usado": wait_actions,
                    "porcentaje": round(wait_percentage, 2)
                },
                "acciones_movimiento": {
                    "veces_usado": move_actions,
                    "porcentaje": round(move_percentage, 2)
                },
                "reglas_mas_usadas": dict(sorted(rules_used.items(), key=lambda x: x[1], reverse=True)[:5]),
                "posicion_final": final_position,
                "alive": alive,
                "parametros": {
                    "K": K,
                    "p": p
                }
            }
        
        return monster_stats
    
    def _calculate_robot_stats(self) -> Dict[str, Any]:
        """
        Calcula estadísticas de todos los robots
        
        Returns:
            Diccionario con estadísticas de robots
        """
        robot_stats = {}
        
        for robot_id, robot_logger in self.robot_loggers.items():
            operations = robot_logger.operations
            
            if not operations:
                continue
            
            # Calcular estadísticas del robot
            total_operations = len(operations)
            rules_used = {}
            memory_usage = 0
            rule_usage = 0
            
            for op in operations:
                rule_num = op.get('rule_num', 0)
                if rule_num > 0:
                    rules_used[rule_num] = rules_used.get(rule_num, 0) + 1
                
                if op.get('uses_memory', 0) == 1:
                    memory_usage += 1
                
                if op.get('uses_rule', 0) == 1:
                    rule_usage += 1
            
            # Calcular porcentajes
            memory_percentage = (memory_usage / total_operations * 100) if total_operations > 0 else 0
            rule_percentage = (rule_usage / total_operations * 100) if total_operations > 0 else 0
            
            robot_stats[f"robot_{robot_id:03d}"] = {
                "total_operaciones": total_operations,
                "uso_memoria": {
                    "veces_usado": memory_usage,
                    "porcentaje": round(memory_percentage, 2)
                },
                "uso_reglas": {
                    "veces_usado": rule_usage,
                    "porcentaje": round(rule_percentage, 2)
                },
                "reglas_mas_usadas": dict(sorted(rules_used.items(), key=lambda x: x[1], reverse=True)[:5]),
                "posicion_final": operations[-1].get('new_position', [0, 0, 0]) if operations else [0, 0, 0],
                "orientacion_final": operations[-1].get('new_orientation', [0, 0, 1]) if operations else [0, 0, 1]
            }
        
        return robot_stats


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
            'Accion_Memoria',      # Acción guardada en memoria
            'Usa_Memoria?',        # 1 si usó memoria, 0 si no
            'Usa_Regla?'           # 1 si usó regla, 0 si no
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
        
        # Nuevos campos para memoria
        memory_action = operation_data.get('memory_action', '')
        uses_memory = operation_data.get('uses_memory', 0)
        uses_rule = operation_data.get('uses_rule', 1)
        
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
            memory_action,                                          # Accion_Memoria
            uses_memory,                                            # Usa_Memoria?
            uses_rule                                               # Usa_Regla?
        ]
        
        # Escribir fila en CSV
        self.csv_writer.writerow(row)
        self.csv_file.flush()  # Asegurar que se escriba inmediatamente
