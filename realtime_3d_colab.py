#!/usr/bin/env python3
"""
Simulación 3D en Tiempo Real de Robots Monstruicidas vs Monstruos
Usa Dash para crear una aplicación web que se actualiza en tiempo real
"""

from jupyter_dash import JupyterDash
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import time
import threading
import socket
import atexit
import signal
import sys
from datetime import datetime
from environment import Environment
from robot import Robot
from monster import Monster
from rule_engine import RuleEngine
from console_formatter import console
from robot_logger import RobotLogger
from monster_logger import MonsterLogger
from config import *

import os, shutil

def ensure_data_files():
    """Garantiza que los archivos CSV de reglas estén disponibles en 'data/'."""

    local_data = os.path.join(os.getcwd(), "data")
    os.makedirs(local_data, exist_ok=True)

    # 1️⃣ los CSV ya están en el repositorio (data/)
    robot_csv = os.path.join(local_data, "robot_rules.csv")
    monster_csv = os.path.join(local_data, "monster_rules.csv")
    if os.path.exists(robot_csv) and os.path.exists(monster_csv):
        print("✅ Archivos CSV encontrados en el repositorio.")
        return

    # 2️⃣ Alternativa: copia automática desde Google Drive (si existe)
    drive_data = "/content/drive/MyDrive/EXAMEN_PARCIAL_FUNDAMENTOS/CODE/data"
    if os.path.exists(drive_data):
        for file in ["robot_rules.csv", "monster_rules.csv"]:
            src = os.path.join(drive_data, file)
            dst = os.path.join(local_data, file)
            if os.path.exists(src):
                shutil.copy(src, dst)
                print(f"📄 Copiado desde Drive: {file}")
        return

    print("⚠️ No se encontraron los archivos CSV de reglas.")
    print("👉 Sube 'robot_rules.csv' y 'monster_rules.csv' a la carpeta 'data/' del proyecto.")
    print("O colócalos en tu Drive en: /content/drive/MyDrive/EXAMEN_PARCIAL_FUNDAMENTOS/CODE/data/")
    raise FileNotFoundError("No se hallaron los archivos de reglas requeridos.")

ensure_data_files()

class RealTimeSimulation:
    def __init__(self):
        self.environment = Environment()
        self.rule_engine = RuleEngine()
        self.monster_logger = MonsterLogger()
        self.robot_logger = RobotLogger(self.monster_logger)
        self.robots = []
        self.monsters = []
        self.step = 0
        self.running = False
        self.app = None
        self.simulation_speed = 1.0  # Velocidad de simulación (multiplicador)
        self.port = None  # Puerto asignado
        self.paused = False  # Estado de pausa
        self.step_mode = False  # Modo paso a paso
        
        # Variables para estadísticas
        self.start_time = None
        self.fecha_inicio = None
        self.monsters_destroyed = 0
        self.robots_destroyed = 0
        
        # Registrar función de limpieza al cerrar
        atexit.register(self.cleanup)
        
        # Manejar señales de interrupción
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def initialize_simulation(self):
        """Inicializa la simulación"""
        console.header("🤖 Simulación 3D en Tiempo Real - Robots Monstruicidas vs Monstruos")
        
        # Cargar reglas
        console.info("Cargando motor de reglas...")
        if not self.rule_engine.load_rules():
            console.error("No se pudieron cargar las reglas CSV")
            return False
        
        # Crear robots y monstruos
        console.info(f"Creando {NUM_ROBOTS} robots y {NUM_MONSTERS} monstruos...")
        
        for i in range(NUM_ROBOTS):
            robot_id = i + 1  # IDs empiezan desde 1
            if ROBOT_POSITION_MODE == "fixed":
                pos = ROBOT_FIXED_POSITION
                console.info(f"Robot {robot_id}: Posición fija {pos}")
            else:
                pos = self.environment.get_random_internal_free_position()
                console.info(f"Robot {robot_id}: Posición aleatoria interna {pos}")
            
            if pos:
                robot = Robot(robot_id, pos, self.environment, self.rule_engine, self.robot_logger)
                self.robots.append(robot)
                self.robot_logger.register_robot(robot_id)
            else:
                console.warning(f"No se pudo crear Robot {robot_id}: No hay posiciones libres internas")
        
        for i in range(NUM_MONSTERS):
            monster_id = i + 1  # IDs empiezan desde 1
            if MONSTER_POSITION_MODE == "fixed":
                pos = MONSTER_FIXED_POSITION
                console.info(f"Monstruo {monster_id}: Posición fija {pos}")
            else:
                pos = self.environment.get_random_internal_free_position()
                console.info(f"Monstruo {monster_id}: Posición aleatoria interna {pos}")
            
            if pos:
                monster = Monster(monster_id, pos, self.environment, self.rule_engine, self.monster_logger)
                self.monsters.append(monster)
                # Registrar monstruo en el logger
                self.monster_logger.register_monster(monster_id)
            else:
                console.warning(f"No se pudo crear Monstruo {monster_id}: No hay posiciones libres internas")
        
        console.success(f"Creados {len(self.robots)} robots y {len(self.monsters)} monstruos")
        
        # Inicializar variables de estadísticas
        self.start_time = time.time()
        self.fecha_inicio = datetime.now().isoformat()
        self.monsters_destroyed = 0
        self.robots_destroyed = 0
        
        return True
    
    def _calculate_final_stats(self):
        """Calcula las estadísticas finales de la simulación"""
        if not self.start_time:
            return None
        
        end_time = time.time()
        duracion = end_time - self.start_time
        alive_robots = sum(1 for r in self.robots if r.alive)
        alive_monsters = sum(1 for m in self.monsters if m.alive)
        
        # Calcular total de monstruos destruidos por robots
        total_monsters_destroyed_by_robots = sum(robot.monsters_destroyed for robot in self.robots)
        
        return {
            "fecha_inicio": self.fecha_inicio,
            "duracion_segundos": round(duracion, 2),
            "pasos_ejecutados": self.step,
            "robots_vivos": alive_robots,
            "robots_muertos": NUM_ROBOTS - alive_robots,
            "monstruos_vivos": alive_monsters,
            "monstruos_eliminados": NUM_MONSTERS - alive_monsters,
            "monstruos_destruidos_por_robots": total_monsters_destroyed_by_robots,
            "monstruos_destruidos_por_colision": self.monsters_destroyed,
            "robots_eliminados": self.robots_destroyed,
            "zonas_libres": self.environment.count_free_zones(),
            "zonas_vacias": self.environment.count_empty_zones(),
            "porcentaje_cobertura": round((self.environment.count_free_zones() / (WORLD_SIZE**3)) * 100, 2)
        }
    
    def create_3d_figure(self):
        """Crea la figura 3D actual"""
        fig = self.environment.visualize(self.robots, self.monsters)
        
        alive_robots = sum(1 for r in self.robots if r.alive)
        alive_monsters = sum(1 for m in self.monsters if m.alive)
        
        fig.update_layout(
            title=f"🤖 Simulación Robots vs Monstruos - Paso {self.step} | Robots: {alive_robots} | Monstruos: {alive_monsters}",
            scene=dict(
                xaxis=dict(range=[0, WORLD_SIZE]),
                yaxis=dict(range=[0, WORLD_SIZE]),
                zaxis=dict(range=[0, WORLD_SIZE])
            ),
            uirevision=UIREVISION  # Mantiene la vista de la cámara entre actualizaciones
        )
        
        return fig
    
    def simulation_loop(self):
        """Bucle principal de la simulación"""
        while self.running and self.step < SIMULATION_STEPS:
            # Verificar si quedan monstruos vivos
            monsters_alive = sum(1 for monster in self.monsters if monster.alive)
            if monsters_alive == 0:
                console.success("¡VICTORIA! Todos los monstruos han sido eliminados!")
                console.info(f"Simulación terminada en el paso {self.step}")
                self.running = False
                break
            
            self.step += 1
            console.step(self.step, SIMULATION_STEPS)
            
            # Ejecutar acciones de robots en secuencia completa
            for robot in self.robots:
                if robot.alive:
                    # Cada robot lee sensores, evalúa regla y actúa en secuencia
                    current_perceptions = robot.perceive()

                    # Obtener el número de regla que se ejecutará
                    rule_number = self.rule_engine.get_robot_rule_number(current_perceptions)
                    
                    action = robot.act(current_perceptions, self.monsters)

                    # Mostrar información del robot usando el nuevo sistema
                    console.robot_action(robot.id, action, tuple(robot.position), rule_number)
                    console.sensor_data(robot.id, current_perceptions, rule_number)
                    
                    # Ejecutar la acción inmediatamente
                    robot.execute_action(action, self.monsters, self.monster_logger)
                    
                    # Obtener percepciones actuales (después del movimiento)
                    current_perceptions = robot.perceive(False)
                    
                    # Predecir siguiente acción basada en percepciones actuales
                    next_action = self.rule_engine.get_robot_action(current_perceptions)
                    next_rule_number = self.rule_engine.get_robot_rule_number(current_perceptions)
                    
                    console.info(f"Próximo movimiento: Regla #{next_rule_number if next_rule_number else 'default'} - Acción: {next_action}")
            
            # Detectar y resolver colisiones entre robots
            self._handle_robot_collisions()
            
            # Ejecutar acciones de monstruos
            for monster in self.monsters:
                if monster.alive:
                    perceptions = monster.perceive()
                    action = monster.act(perceptions)
                    
                    # Información detallada del monstruo
                    steps_remaining = monster.K - monster.steps_since_last_action
                    console.monster_action(monster.id, action, tuple(monster.position), 
                                        monster.K, monster.p, steps_remaining)
            
            # Detectar y resolver colisiones entre monstruos
            self._handle_monster_collisions()
            
            # Mostrar estadísticas
            alive_robots = sum(1 for r in self.robots if r.alive)
            alive_monsters = sum(1 for m in self.monsters if m.alive)
            console.stats(alive_robots, alive_monsters, self.step)
            
            # Verificar si la simulación debe terminar
            if alive_robots == 0:
                console.error("Todos los robots han sido eliminados. Simulación terminada.")
                self.running = False
                
                # Mostrar estadísticas de monstruos destruidos
                self.show_monster_statistics()
                
                # Finalizar logs de robots
                console.info("Finalizando logs de robots...")
                simulation_stats = self._calculate_final_stats()
                self.robot_logger.finalize_all_logs(simulation_stats)
                self.monster_logger.finalize_all_logs(simulation_stats)
                console.success(f"Logs guardados en: {self.robot_logger.output_dir}")
                
                break
            elif alive_monsters == 0:
                console.success("Todos los monstruos han sido eliminados. Simulación terminada.")
                self.running = False
                
                # Mostrar estadísticas de monstruos destruidos
                self.show_monster_statistics()
                
                # Finalizar logs de robots
                console.info("Finalizando logs de robots...")
                simulation_stats = self._calculate_final_stats()
                self.robot_logger.finalize_all_logs(simulation_stats)
                self.monster_logger.finalize_all_logs(simulation_stats)
                console.success(f"Logs guardados en: {self.robot_logger.output_dir}")
                
                break
            
            # Pausa para visualización (ajustada por velocidad)
            delay = REAL_TIME_DELAY / self.simulation_speed
            time.sleep(delay)
        
        if self.step >= SIMULATION_STEPS:
            console.info("Simulación completada - Máximo de pasos alcanzado")
            self.running = False
            
            # Mostrar estadísticas de monstruos destruidos
            self.show_monster_statistics()
    
    def execute_single_step(self):
        """Ejecuta un solo paso de la simulación"""
        if self.step >= SIMULATION_STEPS:
            console.info("Simulación completada - Máximo de pasos alcanzado")
            return False
        
        # Verificar si quedan monstruos vivos
        monsters_alive = sum(1 for monster in self.monsters if monster.alive)
        if monsters_alive == 0:
            console.success("¡VICTORIA! Todos los monstruos han sido eliminados!")
            console.info(f"Simulación terminada en el paso {self.step}")
            return False
        
        self.step += 1
        console.step(self.step, SIMULATION_STEPS)
        
        # Ejecutar acciones de robots en secuencia completa
        for robot in self.robots:
            if robot.alive:
                # Cada robot lee sensores, evalúa regla y actúa en secuencia
                console.info(f"ITERACION Robot {robot.id}: {robot.vacuscope_memory}")

                # Lee los sensores
                current_perceptions = robot.perceive()

                # Obtener el número de regla que se ejecutará
                rule_number = self.rule_engine.get_robot_rule_number(current_perceptions)
                
                action = robot.act(current_perceptions, self.monsters)

                # Mostrar información del robot usando el nuevo sistema
                console.robot_action(robot.id, action, tuple(robot.position), rule_number)
                console.sensor_data(robot.id, current_perceptions, rule_number)
                
                # Ejecutar la acción inmediatamente
                robot.execute_action(action, self.monsters, self.monster_logger)
                
                # Solo mostrar información de regla ejecutada si no es la primera iteración
                if self.step > 1:
                    console.info(f"Regla ejecutada: {rule_number if rule_number else 'Comportamiento por defecto'}")
                    console.info(f"Acción ejecutada: {action}")
                
                # Obtener percepciones actuales (después del movimiento)
                current_perceptions = robot.perceive(False)
                
                # Mostrar información de sensores actuales
                console.sensor_data(robot.id, current_perceptions, rule_number)
                
                # Predecir siguiente acción basada en percepciones actuales
                next_action = self.rule_engine.get_robot_action(current_perceptions)
                next_rule_number = self.rule_engine.get_robot_rule_number(current_perceptions)
                
                console.info(f"Próximo movimiento:")
                console.info(f"  Regla a aplicar: {next_rule_number if next_rule_number else 'Comportamiento por defecto'}")
                console.info(f"  Acción a ejecutar: {next_action}")
                console.info(f"ITERACION Robot {robot.id}: {robot.vacuscope_memory}")
        
        # Ejecutar acciones de monstruos
        for monster in self.monsters:
            if monster.alive:
                perceptions = monster.perceive()
                action = monster.act(perceptions)
                
                # Información detallada del monstruo
                steps_remaining = monster.K - monster.steps_since_last_action
                console.monster_action(monster.id, action, tuple(monster.position), 
                                     monster.K, monster.p, steps_remaining)
        
        # Mostrar estadísticas
        alive_robots = sum(1 for r in self.robots if r.alive)
        alive_monsters = sum(1 for m in self.monsters if m.alive)
        console.stats(alive_robots, alive_monsters, self.step)
        
        # Verificar si la simulación debe terminar
        if alive_robots == 0:
            console.error("Todos los robots han sido eliminados. Simulación terminada.")
            
            # Finalizar logs de robots
            console.info("Finalizando logs de robots...")
            simulation_stats = self._calculate_final_stats()
            self.robot_logger.finalize_all_logs(simulation_stats)
            self.monster_logger.finalize_all_logs(simulation_stats)
            console.success(f"Logs guardados en: {self.robot_logger.output_dir}")
            
            return False
        elif alive_monsters == 0:
            console.success("Todos los monstruos han sido eliminados. Simulación terminada.")
            
            # Finalizar logs de robots
            console.info("Finalizando logs de robots...")
            simulation_stats = self._calculate_final_stats()
            self.robot_logger.finalize_all_logs(simulation_stats)
            self.monster_logger.finalize_all_logs(simulation_stats)
            console.success(f"Logs guardados en: {self.robot_logger.output_dir}")
            
            return False
        
        return True
    
    def _handle_robot_collisions(self):
        """Detecta y resuelve colisiones entre robots"""
        collisions = self.environment.detect_robot_collisions()
        
        for robot_id1, robot_id2 in collisions:
            # Encontrar los robots en la lista
            robot1 = next((r for r in self.robots if r.id == robot_id1), None)
            robot2 = next((r for r in self.robots if r.id == robot_id2), None)
            
            if robot1 and robot2 and robot1.alive and robot2.alive:
                # El robot con menor ID sobrevive, el mayor muere
                survivor = robot1  # robot_id1 < robot_id2 por construcción
                victim = robot2
                
                console.warning(f"🚨 COLISIÓN DETECTADA: {survivor.id_formatted} y {victim.id_formatted} en posición {tuple(survivor.position)}")
                console.info(f"✅ {survivor.id_formatted} sobrevive (menor ID)")
                console.error(f"💀 {victim.id_formatted} muere por colisión")
                
                # Incrementar contador de colisiones del robot que sobrevive
                survivor.robots_collided += 1
                
                # Incrementar contador de robots destruidos
                self.robots_destroyed += 1
                
                # Finalizar log del robot que muere
                if self.robot_logger:
                    self.robot_logger.finalize_robot_log(victim.id)
                
                # Marcar el robot como muerto
                victim.alive = False
                
                # Remover del entorno
                self.environment.robot_positions.pop(victim.id, None)
    
    def _handle_monster_collisions(self):
        """Detecta y resuelve colisiones entre monstruos"""
        collisions = self.environment.detect_monster_collisions()
        
        for monster_id1, monster_id2 in collisions:
            # Encontrar los monstruos en la lista
            monster1 = next((m for m in self.monsters if m.id == monster_id1), None)
            monster2 = next((m for m in self.monsters if m.id == monster_id2), None)
            
            if monster1 and monster2 and monster1.alive and monster2.alive:
                # El monstruo con menor ID sobrevive, el mayor muere
                survivor = monster1  # monster_id1 < monster_id2 por construcción
                victim = monster2
                
                console.warning(f"🚨 COLISIÓN DE MONSTRUOS: {survivor.id_formatted} y {victim.id_formatted} en posición {tuple(survivor.position)}")
                console.info(f"✅ {survivor.id_formatted} sobrevive (menor ID)")
                console.error(f"💀 {victim.id_formatted} muere por colisión")
                
                # Incrementar contador de monstruos destruidos
                self.monsters_destroyed += 1
                
                # Marcar el monstruo como muerto
                victim.alive = False
                
                # Registrar la muerte en el log
                if self.monster_logger:
                    operation_data = {
                        'position': list(victim.position),
                        'perceptions': {},
                        'rule_number': None,
                        'action': 'death_by_collision',
                        'new_position': list(victim.position),
                        'steps_remaining': victim.K - victim.steps_since_last_action,
                        'K': victim.K,
                        'p': victim.p,
                        'alive': False
                    }
                    self.monster_logger.store_monster_operation(victim.id, operation_data)
                
                # Remover del entorno
                self.environment.monster_positions.pop(victim.id, None)
    
    def reset_simulation(self):
        """Reinicia la simulación generando un nuevo mundo y reposicionando agentes"""
        console.info("Reiniciando simulación...")
        
        # Finalizar logs de robots antes de reiniciar
        console.info("Finalizando logs de robots antes del reinicio...")
        self.robot_logger.finalize_all_logs()
        self.monster_logger.finalize_all_logs()
        console.success(f"Logs guardados en: {self.robot_logger.output_dir}")
        
        # Detener simulación actual
        self.running = False
        self.step = 0
        
        # Generar nuevo mundo
        self.environment = Environment()
        
        # Limpiar listas de agentes
        self.robots.clear()
        self.monsters.clear()
        
        # Crear nuevo logger para la nueva simulación
        self.robot_logger = RobotLogger()
        
        # Crear nuevos robots y monstruos
        console.info(f"Creando {NUM_ROBOTS} robots y {NUM_MONSTERS} monstruos...")
        
        for i in range(NUM_ROBOTS):
            robot_id = i + 1  # IDs empiezan desde 1
            if ROBOT_POSITION_MODE == "fixed":
                pos = ROBOT_FIXED_POSITION
                console.info(f"Robot {robot_id}: Posición fija {pos}")
            else:
                pos = self.environment.get_random_internal_free_position()
                console.info(f"Robot {robot_id}: Posición aleatoria interna {pos}")
            
            if pos:
                robot = Robot(robot_id, pos, self.environment, self.rule_engine, self.robot_logger)
                self.robots.append(robot)
                self.robot_logger.register_robot(robot_id)
            else:
                console.warning(f"No se pudo crear Robot {robot_id}: No hay posiciones libres internas")
        
        for i in range(NUM_MONSTERS):
            monster_id = i + 1  # IDs empiezan desde 1
            if MONSTER_POSITION_MODE == "fixed":
                pos = MONSTER_FIXED_POSITION
                console.info(f"Monstruo {monster_id}: Posición fija {pos}")
            else:
                pos = self.environment.get_random_internal_free_position()
                console.info(f"Monstruo {monster_id}: Posición aleatoria interna {pos}")
            
            if pos:
                monster = Monster(monster_id, pos, self.environment, self.rule_engine, self.monster_logger)
                self.monsters.append(monster)
                # Registrar monstruo en el logger
                self.monster_logger.register_monster(monster_id)
            else:
                console.warning(f"No se pudo crear Monstruo {monster_id}: No hay posiciones libres internas")
        
        console.success(f"Simulación reiniciada: {len(self.robots)} robots y {len(self.monsters)} monstruos")
    
    def find_available_port(self, start_port=8050, max_port=8100):
        """
        Encuentra un puerto disponible en el rango especificado
        
        Args:
            start_port: Puerto inicial para buscar
            max_port: Puerto máximo para buscar
            
        Returns:
            int: Puerto disponible o None si no encuentra ninguno
        """
        for port in range(start_port, max_port):
            try:
                # Intentar crear un socket para verificar si el puerto está libre
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('127.0.0.1', port))
                    return port
            except OSError:
                # Puerto ocupado, continuar con el siguiente
                continue
        return None
    
    def show_monster_statistics(self):
        """Muestra estadísticas de monstruos destruidos y colisiones entre robots"""
        console.info("\n📊 ESTADÍSTICAS FINALES DE LA SIMULACIÓN")
        console.info("=" * 60)
        
        total_monsters_destroyed = 0
        total_robots_collided = 0
        robots_with_kills = 0
        robots_with_collisions = 0
        
        for robot in self.robots:
            if robot.monsters_destroyed > 0:
                robots_with_kills += 1
                total_monsters_destroyed += robot.monsters_destroyed
            
            if robot.robots_collided > 0:
                robots_with_collisions += 1
                total_robots_collided += robot.robots_collided
            
            # Mostrar estadísticas individuales
            kills_text = f"{robot.monsters_destroyed} monstruo(s)" if robot.monsters_destroyed > 0 else "0 monstruos"
            collisions_text = f"{robot.robots_collided} robot(s)" if robot.robots_collided > 0 else "0 robots"
            
            if robot.monsters_destroyed > 0 or robot.robots_collided > 0:
                console.success(f"🤖 {robot.id_formatted}: {kills_text} destruido(s), {collisions_text} eliminado(s)")
            else:
                console.info(f"🤖 {robot.id_formatted}: 0 monstruos destruidos, 0 robots eliminados")
        
        console.info("-" * 60)
        console.success(f"🎯 TOTAL DE MONSTRUOS DESTRUIDOS: {total_monsters_destroyed}")
        console.success(f"⚔️ TOTAL DE ROBOTS ELIMINADOS POR COLISIÓN: {total_robots_collided}")
        console.info(f"🏆 ROBOTS CON ELIMINACIONES: {robots_with_kills}/{len(self.robots)}")
        console.info(f"💥 ROBOTS CON COLISIONES: {robots_with_collisions}/{len(self.robots)}")
        
        if robots_with_kills > 0:
            # Encontrar el robot con más eliminaciones de monstruos
            best_monster_killer = max(self.robots, key=lambda r: r.monsters_destroyed)
            console.success(f"🥇 MEJOR CAZADOR: {best_monster_killer.id_formatted} con {best_monster_killer.monsters_destroyed} monstruos")
        
        if robots_with_collisions > 0:
            # Encontrar el robot con más colisiones
            best_collision_killer = max(self.robots, key=lambda r: r.robots_collided)
            console.success(f"🥊 MEJOR COMBATIENTE: {best_collision_killer.id_formatted} con {best_collision_killer.robots_collided} robots eliminados")
        
        console.info("=" * 60)
    
    def cleanup(self):
        """Limpia recursos al cerrar la aplicación"""
        console.info("Limpiando recursos...")
        self.running = False
        
        # Mostrar estadísticas de monstruos destruidos
        self.show_monster_statistics()
        
        # Finalizar logs de robots
        console.info("Finalizando logs de robots...")
        self.robot_logger.finalize_all_logs()
        self.monster_logger.finalize_all_logs()
        console.success(f"Logs guardados en: {self.robot_logger.output_dir}")
        
        if self.port:
            console.info(f"Puerto {self.port} liberado")
    
    def signal_handler(self, signum, frame):
        """Maneja señales de interrupción"""
        console.warning(f"Señal {signum} recibida. Cerrando aplicación...")
        self.cleanup()
        sys.exit(0)
    
    def create_dash_app(self):
        """Crea la aplicación Dash"""
        self.app = JupyterDash(__name__)
        
        self.app.layout = html.Div([
            html.H1("🤖 Simulación Robots vs Monstruos - TIEMPO REAL", 
                   style={'textAlign': 'center', 'margin': '20px'}),
            
            html.Div([
                html.Button('▶️ Iniciar Simulación', id='start-btn', n_clicks=0,
                          style={'margin': '10px', 'padding': '10px 20px', 'fontSize': '16px'}),
                html.Button('⏸️ Pausar', id='pause-btn', n_clicks=0,
                          style={'margin': '10px', 'padding': '10px 20px', 'fontSize': '16px'}),
                html.Button('⏹️ Detener y Reiniciar', id='stop-btn', n_clicks=0,
                          style={'margin': '10px', 'padding': '10px 20px', 'fontSize': '16px', 'backgroundColor': '#ff9800', 'color': 'white'}),
                html.Button('🔄 Reiniciar Mundo', id='reset-btn', n_clicks=0,
                          style={'margin': '10px', 'padding': '10px 20px', 'fontSize': '16px', 'backgroundColor': '#ff6b6b', 'color': 'white'}),
                html.Button('👆 Paso a Paso', id='step-btn', n_clicks=0,
                          style={'margin': '10px', 'padding': '10px 20px', 'fontSize': '16px', 'backgroundColor': '#4caf50', 'color': 'white', 'display': 'none'}),
            ], style={'textAlign': 'center', 'margin': '20px'}),
            
            html.Div([
                html.Label('⚡ Velocidad de Simulación:', style={'fontSize': '16px', 'fontWeight': 'bold'}),
                dcc.Slider(
                    id='speed-slider',
                    min=0.1,
                    max=5.0,
                    step=0.1,
                    value=1.0,
                    marks={
                        0.1: '0.1x',
                        0.5: '0.5x',
                        1.0: '1.0x',
                        2.0: '2.0x',
                        3.0: '3.0x',
                        5.0: '5.0x'
                    },
                    tooltip={"placement": "bottom", "always_visible": True}
                ),
                html.Div(id='speed-display', style={'textAlign': 'center', 'margin': '10px', 'fontSize': '14px'})
            ], style={'margin': '20px', 'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '10px'}),
            
            html.Div(id='status-display', style={'textAlign': 'center', 'margin': '20px', 'fontSize': '18px'}),
            
            dcc.Graph(id='3d-simulation', style={'height': '80vh'}),
            
            dcc.Interval(
                id='interval-component',
                interval=int(REAL_TIME_DELAY * 1000),  # Convertir a milisegundos (se ajustará dinámicamente)
                n_intervals=0,
                disabled=True
            )
        ])
        
        @self.app.callback(
            [Output('3d-simulation', 'figure'),
             Output('status-display', 'children'),
             Output('interval-component', 'disabled'),
             Output('interval-component', 'interval'),
             Output('speed-display', 'children'),
             Output('step-btn', 'style')],
            [Input('interval-component', 'n_intervals'),
             Input('start-btn', 'n_clicks'),
             Input('pause-btn', 'n_clicks'),
             Input('stop-btn', 'n_clicks'),
             Input('reset-btn', 'n_clicks'),
             Input('step-btn', 'n_clicks'),
             Input('speed-slider', 'value')]
        )
        def update_simulation(n_intervals, start_clicks, pause_clicks, stop_clicks, reset_clicks, step_clicks, speed_value):
            ctx = dash.callback_context
            
            if ctx.triggered:
                button_id = ctx.triggered[0]['prop_id'].split('.')[0]
                
                if button_id == 'start-btn' and not self.running:
                    self.running = True
                    self.paused = False
                    self.step_mode = False
                    # Iniciar simulación en un hilo separado
                    simulation_thread = threading.Thread(target=self.simulation_loop)
                    simulation_thread.daemon = True
                    simulation_thread.start()
                    
                elif button_id == 'pause-btn':
                    if self.running and not self.paused:
                        self.paused = True
                        self.running = False
                    elif self.paused:
                        self.paused = False
                        self.running = True
                        self.step_mode = False
                        # Reanudar simulación
                        simulation_thread = threading.Thread(target=self.simulation_loop)
                        simulation_thread.daemon = True
                        simulation_thread.start()
                    
                elif button_id == 'stop-btn':
                    self.running = False
                    self.paused = False
                    self.step_mode = False
                    self.step = 0
                    
                    # Mostrar estadísticas al detener
                    self.show_monster_statistics()
                    
                elif button_id == 'reset-btn':
                    # Reiniciar simulación
                    self.reset_simulation()
                    
                elif button_id == 'step-btn':
                    # Ejecutar paso a paso
                    if self.paused:
                        self.execute_single_step()
                    
                elif button_id == 'speed-slider':
                    # Actualizar velocidad de simulación
                    self.simulation_speed = speed_value
            
            # Crear figura actualizada
            fig = self.create_3d_figure()
            
            # Estado actual
            alive_robots = sum(1 for r in self.robots if r.alive)
            alive_monsters = sum(1 for m in self.monsters if m.alive)
            
            if self.running:
                status = f"🔄 Simulación ejecutándose... Paso {self.step} | Robots: {alive_robots} | Monstruos: {alive_monsters}"
                interval_disabled = False
                step_btn_style = {'margin': '10px', 'padding': '10px 20px', 'fontSize': '16px', 'backgroundColor': '#4caf50', 'color': 'white', 'display': 'none'}
            elif self.paused:
                status = f"⏸️ Simulación pausada | Paso {self.step} | Robots: {alive_robots} | Monstruos: {alive_monsters}"
                interval_disabled = True
                step_btn_style = {'margin': '10px', 'padding': '10px 20px', 'fontSize': '16px', 'backgroundColor': '#4caf50', 'color': 'white', 'display': 'inline-block'}
            else:
                status = f"⏹️ Simulación detenida | Paso {self.step} | Robots: {alive_robots} | Monstruos: {alive_monsters}"
                interval_disabled = True
                step_btn_style = {'margin': '10px', 'padding': '10px 20px', 'fontSize': '16px', 'backgroundColor': '#4caf50', 'color': 'white', 'display': 'none'}
            
            # Calcular intervalo dinámico basado en velocidad
            dynamic_interval = int(REAL_TIME_DELAY * 1000 / self.simulation_speed)
            
            # Mostrar información de velocidad
            speed_display = f"Velocidad actual: {self.simulation_speed:.1f}x | Intervalo: {dynamic_interval}ms"
            
            return fig, status, interval_disabled, dynamic_interval, speed_display, step_btn_style
    
    def run(self):
        """Ejecuta la simulación completa (versión Colab-compatible)"""
        if not self.initialize_simulation():
            return

        print("\n🎬 Configurando aplicación web...")
        self.create_dash_app()

        # Intentar asignar puerto disponible
        self.port = self.find_available_port()
        if not self.port:
            console.error("No se encontró ningún puerto disponible en el rango 8050-8100")
            return

        console.info("✅ Servidor Dash listo para ejecutarse en Colab")
        console.info("🔹 Usa los botones para controlar la simulación")
        console.info("🔹 La aplicación se mostrará directamente en esta celda (modo inline)")

        try:
            # 🚀 Mostrar la aplicación directamente dentro del notebook
            self.app.run_server(mode='inline', port=self.port)
        except KeyboardInterrupt:
            console.warning("Servidor detenido por el usuario")
        except Exception as e:
            console.error(f"Error iniciando servidor: {e}")
        finally:
            self.cleanup()


if __name__ == "__main__":
    sim = RealTimeSimulation()
    sim.run()  # Ejecutar sin asignar ni devolver nada explícitamente
    raise SystemExit  # ← evita que Colab re-renderice la salida automáticamente
