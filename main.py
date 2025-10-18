#!/usr/bin/env python3
"""
Simulación de Robots Monstruicidas vs Monstruos
Sistema con motor de reglas CSV para comportamiento de agentes
SIMULACIÓN EN TIEMPO REAL CON ANIMACIÓN
"""

import sys
import os
import time
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from environment import Environment
from robot import Robot
from monster import Monster
from rule_engine import RuleEngine
from console_formatter import console
from robot_logger import RobotLogger
from config import *

def main(show_visualization: bool = True, real_time: bool = True):
    """
    Función principal de la simulación
    
    Args:
        show_visualization: Si mostrar la visualización 3D
        real_time: Si ejecutar en tiempo real con animación
    """
    console.header("🤖 Simulación de Robots Monstruicidas vs Monstruos")
    
    # Inicializar motor de reglas
    console.info("Cargando motor de reglas...")
    rule_engine = RuleEngine()
    
    if not rule_engine.load_rules():
        console.error("No se pudieron cargar las reglas CSV")
        console.warning("Verifica que los archivos existan en la carpeta 'data/'")
        return
    
    # Mostrar resumen de reglas
    rule_engine.print_rules_summary()
    
    # Validar reglas
    errors = rule_engine.validate_rules()
    if errors['robot'] or errors['monster']:
        console.warning("Advertencias en las reglas:")
        for agent_type, error_list in errors.items():
            if error_list:
                console.warning(f"{agent_type}: {', '.join(error_list)}")
    
    # Crear entorno
    console.info("Creando entorno 3D...")
    environment = Environment()
    
    # Inicializar sistema de logging
    console.info("Inicializando sistema de logging...")
    robot_logger = RobotLogger()
    console.success(f"Sistema de logging inicializado: {robot_logger.simulation_id}")
    
    # Crear robots con motor de reglas
    console.info(f"Creando {NUM_ROBOTS} robots y {NUM_MONSTERS} monstruos...")
    robots = []
    monsters = []
    
    for i in range(NUM_ROBOTS):
        if ROBOT_POSITION_MODE == "fixed":
            pos = ROBOT_FIXED_POSITION
        else:
            pos = environment.get_random_internal_free_position()
        
        if pos:
            robot = Robot(i, pos, environment, rule_engine, robot_logger)
            robots.append(robot)
            # Registrar robot en el logger
            robot_logger.register_robot(i)
    
    for i in range(NUM_MONSTERS):
        if MONSTER_POSITION_MODE == "fixed":
            pos = MONSTER_FIXED_POSITION
        else:
            pos = environment.get_random_internal_free_position()
        
        if pos:
            monster = Monster(i, pos, environment, rule_engine)
            monsters.append(monster)
    
    console.success(f"Creados {len(robots)} robots y {len(monsters)} monstruos")
    
    # Mostrar posiciones iniciales
    console.subheader("📍 Posiciones iniciales")
    
    robot_positions = [f"Robot {robot.id}: Posición {tuple(robot.position)} - Estado: {'Vivo' if robot.alive else 'Muerto'}" 
                      for robot in robots if robot.alive]
    console.list_items(robot_positions, f"🤖 ROBOTS ({len(robots)})")
    
    monster_positions = [f"Monstruo {monster.id}: Posición {tuple(monster.position)} - Estado: {'Vivo' if monster.alive else 'Muerto'}" 
                       for monster in monsters if monster.alive]
    console.list_items(monster_positions, f"👹 MONSTRUOS ({len(monsters)})")
    
    if real_time and show_visualization:
        console.info(f"Iniciando simulación en TIEMPO REAL por {SIMULATION_STEPS} pasos...")
        console.info("Presiona Ctrl+C para detener la simulación")
        run_real_time_simulation(environment, robots, monsters, rule_engine, robot_logger)
    else:
        # Ejecutar simulación tradicional
        console.info(f"Iniciando simulación por {SIMULATION_STEPS} pasos...")
        run_simulation(environment, robots, monsters, rule_engine, robot_logger)
        
        # Mostrar resultados finales
        console.subheader("📈 Resultados finales")
        console.info(f"Pasos ejecutados: {SIMULATION_STEPS}")
        console.info(f"Robots vivos: {sum(1 for r in robots if r.alive)}")
        console.info(f"Monstruos vivos: {sum(1 for m in monsters if m.alive)}")
        
        for robot in robots:
            if robot.alive:
                console.info(f"Robot {robot.id}: {robot.get_memory_size()} experiencias en memoria")
        
        # Generar visualización si se solicita
        if show_visualization:
            console.info("Generando visualización 3D...")
            try:
                fig = environment.visualize(robots, monsters)
                fig.show()
                console.success("Visualización mostrada en el navegador")
            except Exception as e:
                console.error(f"Error al mostrar visualización: {e}")
                console.info("Guardando visualización como archivo HTML...")
                try:
                    fig.write_html("simulacion.html")
                    console.success("Visualización guardada como 'simulacion.html'")
                except Exception as e2:
                    console.error(f"Error guardando archivo: {e2}")

def run_real_time_simulation(environment, robots, monsters, rule_engine, robot_logger):
    """
    Ejecuta la simulación en tiempo real con visualización 3D actualizada en vivo
    Usa Plotly con actualización dinámica en una sola ventana del navegador
    
    Args:
        environment: Entorno de la simulación
        robots: Lista de robots
        monsters: Lista de monstruos
        rule_engine: Motor de reglas
    """
    try:
        console.info("Iniciando simulación 3D en TIEMPO REAL...")
        console.info("Se abrirá una ventana del navegador que se actualizará en vivo")
        console.info("Verás el movimiento de robots y monstruos paso a paso")
        console.info("Presiona Ctrl+C para detener")
        
        # Crear figura inicial
        fig = environment.visualize(robots, monsters)
        fig.update_layout(
            title="🤖 Simulación Robots vs Monstruos - TIEMPO REAL",
            updatemenus=[{
                "type": "buttons",
                "buttons": [
                    {"label": "⏸️ Pausar", "method": "animate", "args": [[None], {"frame": {"duration": 0, "redraw": False}}]}
                ]
            }]
        )
        
        # Mostrar figura inicial
        fig.show()
        console.success("Ventana del navegador abierta - La simulación comenzará ahora")
        
        # Ejecutar simulación paso a paso con actualización en vivo
        step = 0
        while step < SIMULATION_STEPS:
            step += 1
            console.step(step, SIMULATION_STEPS)
            
            # Ejecutar acciones de robots
            for robot in robots:
                if robot.alive:
                    perceptions = robot.perceive()
                    action = robot.act(perceptions)
                    console.robot_action(robot.id, action, tuple(robot.position))
            
            # Ejecutar acciones de monstruos
            for monster in monsters:
                if monster.alive:
                    perceptions = monster.perceive()
                    action = monster.act(perceptions)
                    steps_remaining = monster.K - monster.steps_since_last_action
                    console.monster_action(monster.id, action, tuple(monster.position), 
                                         monster.K, monster.p, steps_remaining)
            
            # Mostrar estadísticas
            alive_robots = sum(1 for r in robots if r.alive)
            alive_monsters = sum(1 for m in monsters if m.alive)
            console.stats(alive_robots, alive_monsters, step)
            
            # Actualizar visualización 3D en tiempo real
            try:
                # Crear nueva figura con estado actualizado
                fig = environment.visualize(robots, monsters)
                fig.update_layout(
                    title=f"🤖 Simulación Robots vs Monstruos - Paso {step} | Robots: {alive_robots} | Monstruos: {alive_monsters}"
                )
                
                # Actualizar la figura existente (esto debería actualizar la ventana abierta)
                fig.show()
                
            except Exception as e:
                console.warning(f"Error actualizando visualización: {e}")
            
            # Verificar si la simulación debe terminar
            if alive_robots == 0:
                console.error("Todos los robots han sido eliminados. Simulación terminada.")
                break
            elif alive_monsters == 0:
                console.success("Todos los monstruos han sido eliminados. Simulación terminada.")
                break
            
            # Pausa para visualización
            time.sleep(REAL_TIME_DELAY)  # Pausa configurable entre pasos
        
        console.success("Simulación completada. La visualización final permanece abierta.")
        
        # Finalizar logs de todos los robots
        console.info("Finalizando logs de robots...")
        robot_logger.finalize_all_logs()
        console.success(f"Logs guardados en: {robot_logger.output_dir}")
            
    except KeyboardInterrupt:
        console.warning("Simulación detenida por el usuario")
        # Finalizar logs incluso si se interrumpe
        console.info("Finalizando logs de robots...")
        robot_logger.finalize_all_logs()
        console.success(f"Logs guardados en: {robot_logger.output_dir}")
    except Exception as e:
        console.error(f"Error en simulación en tiempo real: {e}")
        # Finalizar logs incluso si hay error
        console.info("Finalizando logs de robots...")
        robot_logger.finalize_all_logs()
        console.success(f"Logs guardados en: {robot_logger.output_dir}")

def run_simulation(environment, robots, monsters, rule_engine, robot_logger):
    """
    Ejecuta la simulación paso a paso
    
    Args:
        environment: Entorno de la simulación
        robots: Lista de robots
        monsters: Lista de monstruos
        rule_engine: Motor de reglas
    """
    for step in range(1, SIMULATION_STEPS + 1):
        console.step(step, SIMULATION_STEPS)
        
        # Ejecutar acciones de robots
        for robot in robots:
            if robot.alive:
                perceptions = robot.perceive()
                action = robot.act(perceptions)
                console.robot_action(robot.id, action, tuple(robot.position))
        
        # Ejecutar acciones de monstruos
        for monster in monsters:
            if monster.alive:
                perceptions = monster.perceive()
                action = monster.act(perceptions)
                steps_remaining = monster.K - monster.steps_since_last_action
                console.monster_action(monster.id, action, tuple(monster.position), 
                                     monster.K, monster.p, steps_remaining)
        
        # Mostrar estadísticas cada 10 pasos
        alive_robots = sum(1 for r in robots if r.alive)
        alive_monsters = sum(1 for m in monsters if m.alive)
        console.stats(alive_robots, alive_monsters, step)
        
        if step % 10 == 0:
            robot_details = [f"Robot {robot.id}: {tuple(robot.position)}" 
                           for robot in robots if robot.alive]
            console.list_items(robot_details, "🤖 Robots vivos")
            
            monster_details = [f"Monstruo {monster.id}: {tuple(monster.position)}" 
                             for monster in monsters if monster.alive]
            console.list_items(monster_details, "👹 Monstruos vivos")
        
        # Verificar si la simulación debe terminar
        if alive_robots == 0:
            console.error("Todos los robots han sido eliminados. Simulación terminada.")
            break
        elif alive_monsters == 0:
            console.success("Todos los monstruos han sido eliminados. Simulación terminada.")
            break
    
    # Finalizar logs de todos los robots
    console.info("Finalizando logs de robots...")
    robot_logger.finalize_all_logs()
    console.success(f"Logs guardados en: {robot_logger.output_dir}")

if __name__ == "__main__":
    # Verificar argumentos de línea de comandos
    show_viz = "--no-viz" not in sys.argv
    real_time = "--real-time" in sys.argv or "--rt" in sys.argv
    static = "--static" in sys.argv
    
    # Por defecto usar tiempo real si no se especifica static
    if not static and not real_time:
        real_time = True
    
    # Si se especifica static, desactivar tiempo real
    if static:
        real_time = False
    
    console.info(f"Modo: {'TIEMPO REAL' if real_time else 'ESTÁTICO'}")
    console.info(f"Visualización: {'ACTIVADA' if show_viz else 'DESACTIVADA'}")
    
    main(show_visualization=show_viz, real_time=real_time)