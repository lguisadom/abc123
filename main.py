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
from config import *

def main(show_visualization: bool = True, real_time: bool = True):
    """
    Función principal de la simulación
    
    Args:
        show_visualization: Si mostrar la visualización 3D
        real_time: Si ejecutar en tiempo real con animación
    """
    print("🤖 Simulación de Robots Monstruicidas vs Monstruos")
    print("=" * 50)
    
    # Inicializar motor de reglas
    print("📋 Cargando motor de reglas...")
    rule_engine = RuleEngine()
    
    if not rule_engine.load_rules():
        print("❌ Error: No se pudieron cargar las reglas CSV")
        print("   Verifica que los archivos existan en la carpeta 'data/'")
        return
    
    # Mostrar resumen de reglas
    rule_engine.print_rules_summary()
    
    # Validar reglas
    errors = rule_engine.validate_rules()
    if errors['robot'] or errors['monster']:
        print("⚠️ Advertencias en las reglas:")
        for agent_type, error_list in errors.items():
            if error_list:
                print(f"   {agent_type}: {', '.join(error_list)}")
    
    # Crear entorno
    print("\n🌍 Creando entorno 3D...")
    environment = Environment()
    
    # Crear robots con motor de reglas
    print(f"\n🤖 Creando {NUM_ROBOTS} robots y {NUM_MONSTERS} monstruos...")
    robots = []
    monsters = []
    
    for i in range(NUM_ROBOTS):
        pos = environment.get_random_free_position()
        if pos:
            robot = Robot(i, pos, environment, rule_engine)
            robots.append(robot)
    
    for i in range(NUM_MONSTERS):
        pos = environment.get_random_free_position()
        if pos:
            monster = Monster(i, pos, environment, rule_engine)
            monsters.append(monster)
    
    print(f"✅ Creados {len(robots)} robots y {len(monsters)} monstruos")
    
    # Mostrar posiciones iniciales
    print("\n📍 Posiciones iniciales:")
    print(f"   🤖 ROBOTS ({len(robots)}):")
    for robot in robots:
        if robot.alive:
            print(f"      Robot {robot.id}: Posición {tuple(robot.position)} - Estado: {'Vivo' if robot.alive else 'Muerto'}")
    
    print(f"   👹 MONSTRUOS ({len(monsters)}):")
    for monster in monsters:
        if monster.alive:
            print(f"      Monstruo {monster.id}: Posición {tuple(monster.position)} - Estado: {'Vivo' if monster.alive else 'Muerto'}")
    
    if real_time and show_visualization:
        print(f"\n🚀 Iniciando simulación en TIEMPO REAL por {SIMULATION_STEPS} pasos...")
        print("💡 Presiona Ctrl+C para detener la simulación")
        run_real_time_simulation(environment, robots, monsters, rule_engine)
    else:
        # Ejecutar simulación tradicional
        print(f"\n🚀 Iniciando simulación por {SIMULATION_STEPS} pasos...")
        run_simulation(environment, robots, monsters, rule_engine)
        
        # Mostrar resultados finales
        print("\n📈 Resultados finales:")
        print(f"   • Pasos ejecutados: {SIMULATION_STEPS}")
        print(f"   • Robots vivos: {sum(1 for r in robots if r.alive)}")
        print(f"   • Monstruos vivos: {sum(1 for m in monsters if m.alive)}")
        
        for robot in robots:
            if robot.alive:
                print(f"   • Robot {robot.id}: {robot.get_memory_size()} experiencias en memoria")
        
        # Generar visualización si se solicita
        if show_visualization:
            print("\n🎨 Generando visualización 3D...")
            try:
                fig = environment.visualize(robots, monsters)
                fig.show()
                print("✅ Visualización mostrada en el navegador")
            except Exception as e:
                print(f"⚠️ Error al mostrar visualización: {e}")
                print("💾 Guardando visualización como archivo HTML...")
                try:
                    fig.write_html("simulacion.html")
                    print("✅ Visualización guardada como 'simulacion.html'")
                except Exception as e2:
                    print(f"❌ Error guardando archivo: {e2}")

def run_real_time_simulation(environment, robots, monsters, rule_engine):
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
        print("🎬 Iniciando simulación 3D en TIEMPO REAL...")
        print("💡 Se abrirá una ventana del navegador que se actualizará en vivo")
        print("💡 Verás el movimiento de robots y monstruos paso a paso")
        print("💡 Presiona Ctrl+C para detener")
        
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
        print("✅ Ventana del navegador abierta - La simulación comenzará ahora")
        
        # Ejecutar simulación paso a paso con actualización en vivo
        step = 0
        while step < SIMULATION_STEPS:
            step += 1
            print(f"\n--- Paso {step} ---")
            
            # Ejecutar acciones de robots
            for robot in robots:
                if robot.alive:
                    perceptions = robot.perceive()
                    action = robot.act(perceptions)
                    print(f"Robot {robot.id}: {action}")
            
            # Ejecutar acciones de monstruos
            for monster in monsters:
                if monster.alive:
                    perceptions = monster.perceive()
                    action = monster.act(perceptions)
                    print(f"Monstruo {monster.id}: {action}")
            
            # Mostrar estadísticas
            alive_robots = sum(1 for r in robots if r.alive)
            alive_monsters = sum(1 for m in monsters if m.alive)
            print(f"📊 Estado: {alive_robots} robots vivos, {alive_monsters} monstruos vivos")
            
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
                print(f"⚠️ Error actualizando visualización: {e}")
            
            # Verificar si la simulación debe terminar
            if alive_robots == 0:
                print("🏁 Todos los robots han sido eliminados. Simulación terminada.")
                break
            elif alive_monsters == 0:
                print("🏁 Todos los monstruos han sido eliminados. Simulación terminada.")
                break
            
            # Pausa para visualización
            time.sleep(REAL_TIME_DELAY)  # Pausa configurable entre pasos
        
        print("\n🎨 Simulación completada. La visualización final permanece abierta.")
            
    except KeyboardInterrupt:
        print("\n⏹️ Simulación detenida por el usuario")
    except Exception as e:
        print(f"❌ Error en simulación en tiempo real: {e}")

def run_simulation(environment, robots, monsters, rule_engine):
    """
    Ejecuta la simulación paso a paso
    
    Args:
        environment: Entorno de la simulación
        robots: Lista de robots
        monsters: Lista de monstruos
        rule_engine: Motor de reglas
    """
    for step in range(1, SIMULATION_STEPS + 1):
        print(f"\n--- Paso {step} ---")
        
        # Ejecutar acciones de robots
        for robot in robots:
            if robot.alive:
                perceptions = robot.perceive()
                action = robot.act(perceptions)
                print(f"Robot {robot.id}: {action}")
        
        # Ejecutar acciones de monstruos
        for monster in monsters:
            if monster.alive:
                perceptions = monster.perceive()
                action = monster.act(perceptions)
                print(f"Monstruo {monster.id}: {action}")
        
        # Mostrar estadísticas cada 10 pasos
        alive_robots = sum(1 for r in robots if r.alive)
        alive_monsters = sum(1 for m in monsters if m.alive)
        print(f"📊 Estado: {alive_robots} robots vivos, {alive_monsters} monstruos vivos")
        
        if step % 10 == 0:
            print(f"   🤖 Robots vivos:")
            for robot in robots:
                if robot.alive:
                    print(f"      Robot {robot.id}: {tuple(robot.position)}")
            
            print(f"   👹 Monstruos vivos:")
            for monster in monsters:
                if monster.alive:
                    print(f"      Monstruo {monster.id}: {tuple(monster.position)}")
        
        # Verificar si la simulación debe terminar
        if alive_robots == 0:
            print("🏁 Todos los robots han sido eliminados. Simulación terminada.")
            break
        elif alive_monsters == 0:
            print("🏁 Todos los monstruos han sido eliminados. Simulación terminada.")
            break

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
    
    print(f"🎮 Modo: {'TIEMPO REAL' if real_time else 'ESTÁTICO'}")
    print(f"🎨 Visualización: {'ACTIVADA' if show_viz else 'DESACTIVADA'}")
    
    main(show_visualization=show_viz, real_time=real_time)