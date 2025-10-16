#!/usr/bin/env python3
"""
Simulación 3D en Tiempo Real de Robots Monstruicidas vs Monstruos
Usa Dash para crear una aplicación web que se actualiza en tiempo real
"""

import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import time
import threading
import webbrowser
import socket
import atexit
import signal
import sys
from environment import Environment
from robot import Robot
from monster import Monster
from rule_engine import RuleEngine
from config import *

class RealTimeSimulation:
    def __init__(self):
        self.environment = Environment()
        self.rule_engine = RuleEngine()
        self.robots = []
        self.monsters = []
        self.step = 0
        self.running = False
        self.app = None
        self.simulation_speed = 1.0  # Velocidad de simulación (multiplicador)
        self.port = None  # Puerto asignado
        self.paused = False  # Estado de pausa
        self.step_mode = False  # Modo paso a paso
        
        # Registrar función de limpieza al cerrar
        atexit.register(self.cleanup)
        
        # Manejar señales de interrupción
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def initialize_simulation(self):
        """Inicializa la simulación"""
        print("🤖 Simulación 3D en Tiempo Real - Robots Monstruicidas vs Monstruos")
        print("=" * 70)
        
        # Cargar reglas
        print("📋 Cargando motor de reglas...")
        if not self.rule_engine.load_rules():
            print("❌ Error: No se pudieron cargar las reglas CSV")
            return False
        
        # Crear robots y monstruos
        print(f"\n🤖 Creando {NUM_ROBOTS} robots y {NUM_MONSTERS} monstruos...")
        
        for i in range(NUM_ROBOTS):
            if ROBOT_POSITION_MODE == "fixed":
                pos = ROBOT_FIXED_POSITION
                print(f"   Robot {i}: Posición fija {pos}")
            else:
                pos = self.environment.get_random_internal_free_position()
                print(f"   Robot {i}: Posición aleatoria interna {pos}")
            
            if pos:
                robot = Robot(i, pos, self.environment, self.rule_engine)
                self.robots.append(robot)
            else:
                print(f"   ⚠️ No se pudo crear Robot {i}: No hay posiciones libres internas")
        
        for i in range(NUM_MONSTERS):
            if MONSTER_POSITION_MODE == "fixed":
                pos = MONSTER_FIXED_POSITION
                print(f"   Monstruo {i}: Posición fija {pos}")
            else:
                pos = self.environment.get_random_internal_free_position()
                print(f"   Monstruo {i}: Posición aleatoria interna {pos}")
            
            if pos:
                monster = Monster(i, pos, self.environment, self.rule_engine)
                self.monsters.append(monster)
            else:
                print(f"   ⚠️ No se pudo crear Monstruo {i}: No hay posiciones libres internas")
        
        print(f"✅ Creados {len(self.robots)} robots y {len(self.monsters)} monstruos")
        return True
    
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
                print(f"\n🎉 ¡VICTORIA! Todos los monstruos han sido eliminados!")
                print(f"📊 Simulación terminada en el paso {self.step}")
                self.running = False
                break
            
            self.step += 1
            print(f"\n--- Paso {self.step} ---")
            
            # Ejecutar acciones de robots en secuencia completa
            for robot in self.robots:
                if robot.alive:
                    # Cada robot lee sensores, evalúa regla y actúa en secuencia
                    current_perceptions = robot.perceive()

                    # Obtener el número de regla que se ejecutará
                    rule_number = self.rule_engine.get_robot_rule_number(current_perceptions)
                    
                    action = robot.act(current_perceptions, self.monsters)

                    # Información de sensores actuales en formato compacto
                    sensor_parts = []
                    for sensor, value in current_perceptions.items():
                        if sensor != "Energometro" and sensor != "Roboscanner_Front":
                            sensor_parts.append(f"{sensor}={value}")
                    
                    sensor_string = ", ".join(sensor_parts)
                    print(f"🤖 Robot {robot.id}:")
                    print(f"  🔍 [regla #{rule_number if rule_number else 'default'}, {sensor_string}, Accion={action}]")
                    print(f"  📋 Regla a ejecutar: {rule_number if rule_number else 'Comportamiento por defecto'}")
                    print(f"  ⚡ Acción a ejecutar: {action}")
                    
                    # Ejecutar la acción inmediatamente
                    robot.execute_action(action, self.monsters)
                    
                    # Información del robot DESPUÉS de ejecutar la acción
                    print(f"🤖 Robot {robot.id}:")
                    print(f"  📍 Posición actual: {robot.position}")
                    
                    # Obtener percepciones actuales (después del movimiento)
                    current_perceptions = robot.perceive(False)
                    
                    # Información de sensores actuales en formato compacto
                    sensor_parts = []
                    for sensor, value in current_perceptions.items():
                        if sensor != "Energometro" and sensor != "Roboscanner_Front":
                            sensor_parts.append(f"{sensor}={value}")
                    
                    sensor_string = ", ".join(sensor_parts)
                    print(f"  🔍 [regla #{rule_number if rule_number else 'default'}, {sensor_string}, Accion={action}]")
                    
                    # Predecir siguiente acción basada en percepciones actuales
                    next_action = self.rule_engine.get_robot_action(current_perceptions)
                    next_rule_number = self.rule_engine.get_robot_rule_number(current_perceptions)
                    
                    print(f"  🔮 Próximo movimiento:")
                    print(f"    Regla a aplicar: {next_rule_number if next_rule_number else 'Comportamiento por defecto'}")
                    print(f"    Acción a ejecutar: {next_action}")
            
            # Ejecutar acciones de monstruos
            for monster in self.monsters:
                if monster.alive:
                    perceptions = monster.perceive()
                    action = monster.act(perceptions)
                    
                    # Información detallada del monstruo
                    steps_remaining = monster.K - monster.steps_since_last_action
                    print(f"Monstruo {monster.id}: pos {monster.position} - acción a ejecutar: [{action}] - K={monster.K}, p={monster.p}, pasos_restantes={steps_remaining}")
            
            # Mostrar estadísticas
            alive_robots = sum(1 for r in self.robots if r.alive)
            alive_monsters = sum(1 for m in self.monsters if m.alive)
            print(f"📊 Estado: {alive_robots} robots vivos, {alive_monsters} monstruos vivos")
            
            # Verificar si la simulación debe terminar
            if alive_robots == 0:
                print("🏁 Todos los robots han sido eliminados. Simulación terminada.")
                self.running = False
                break
            elif alive_monsters == 0:
                print("🏁 Todos los monstruos han sido eliminados. Simulación terminada.")
                self.running = False
                break
            
            # Pausa para visualización (ajustada por velocidad)
            delay = REAL_TIME_DELAY / self.simulation_speed
            time.sleep(delay)
        
        if self.step >= SIMULATION_STEPS:
            print("🏁 Simulación completada - Máximo de pasos alcanzado")
            self.running = False
    
    def execute_single_step(self):
        """Ejecuta un solo paso de la simulación"""
        if self.step >= SIMULATION_STEPS:
            print("🏁 Simulación completada - Máximo de pasos alcanzado")
            return False
        
        # Verificar si quedan monstruos vivos
        monsters_alive = sum(1 for monster in self.monsters if monster.alive)
        if monsters_alive == 0:
            print(f"\n🎉 ¡VICTORIA! Todos los monstruos han sido eliminados!")
            print(f"📊 Simulación terminada en el paso {self.step}")
            return False
        
        self.step += 1
        print(f"\n--- Paso {self.step} (Paso a Paso) ---")
        
        # Ejecutar acciones de robots en secuencia completa
        for robot in self.robots:
            if robot.alive:
                # Cada robot lee sensores, evalúa regla y actúa en secuencia
                print(f"🤖 ******* ITERACION Robot {robot.id}: {robot.vacuscope_memory}")
                current_perceptions = robot.perceive()

                # Obtener el número de regla que se ejecutará
                rule_number = self.rule_engine.get_robot_rule_number(current_perceptions)
                
                action = robot.act(current_perceptions, self.monsters)

                # Información de sensores actuales en formato compacto
                sensor_parts = []
                for sensor, value in current_perceptions.items():
                    if sensor != "Energometro" and sensor != "Roboscanner_Front":
                        sensor_parts.append(f"{sensor}={value}")
                
                sensor_string = ", ".join(sensor_parts)
                print(f"🤖 Robot {robot.id}:")
                print(f"  🔍 [regla #{rule_number if rule_number else 'default'}, {sensor_string}, Accion={action}]")
                print(f"  📋 Regla a ejecutar: {rule_number if rule_number else 'Comportamiento por defecto'}")
                print(f"  ⚡ Acción a ejecutar: {action}")
                
                # Ejecutar la acción inmediatamente
                robot.execute_action(action, self.monsters)
                
                # Información del robot DESPUÉS de ejecutar la acción
                print(f"🤖 Robot {robot.id}:")
                print(f"  📍 Posición actual: {robot.position}")
                
                # Solo mostrar información de regla ejecutada si no es la primera iteración
                if self.step > 1:
                    print(f"  📋 Regla ejecutada: {rule_number if rule_number else 'Comportamiento por defecto'}")
                    print(f"  ⚡ Acción ejecutada: {action}")
                
                # Obtener percepciones actuales (después del movimiento)
                current_perceptions = robot.perceive(False)
                
                # Información de sensores actuales en formato compacto
                sensor_parts = []
                for sensor, value in current_perceptions.items():
                    if sensor != "Energometro" and sensor != "Roboscanner_Front":
                        sensor_parts.append(f"{sensor}={value}")
                
                sensor_string = ", ".join(sensor_parts)
                print(f"  🔍 [regla #{rule_number if rule_number else 'default'}, {sensor_string}, Accion={action}]")
                
                # Predecir siguiente acción basada en percepciones actuales
                next_action = self.rule_engine.get_robot_action(current_perceptions)
                next_rule_number = self.rule_engine.get_robot_rule_number(current_perceptions)
                
                print(f"  🔮 Próximo movimiento:")
                print(f"    Regla a aplicar: {next_rule_number if next_rule_number else 'Comportamiento por defecto'}")
                print(f"    Acción a ejecutar: {next_action}")
                print(f"🤖 ******* ITERACION Robot {robot.id}: {robot.vacuscope_memory}")
        
        # Ejecutar acciones de monstruos
        for monster in self.monsters:
            if monster.alive:
                perceptions = monster.perceive()
                action = monster.act(perceptions)
                
                # Información detallada del monstruo
                steps_remaining = monster.K - monster.steps_since_last_action
                print(f"Monstruo {monster.id}: pos {monster.position} - acción a ejecutar: [{action}] - K={monster.K}, p={monster.p}, pasos_restantes={steps_remaining}")
        
        # Mostrar estadísticas
        alive_robots = sum(1 for r in self.robots if r.alive)
        alive_monsters = sum(1 for m in self.monsters if m.alive)
        print(f"📊 Estado: {alive_robots} robots vivos, {alive_monsters} monstruos vivos")
        
        # Verificar si la simulación debe terminar
        if alive_robots == 0:
            print("🏁 Todos los robots han sido eliminados. Simulación terminada.")
            return False
        elif alive_monsters == 0:
            print("🏁 Todos los monstruos han sido eliminados. Simulación terminada.")
            return False
        
        return True
    
    def reset_simulation(self):
        """Reinicia la simulación generando un nuevo mundo y reposicionando agentes"""
        print("\n🔄 Reiniciando simulación...")
        
        # Detener simulación actual
        self.running = False
        self.step = 0
        
        # Generar nuevo mundo
        self.environment = Environment()
        
        # Limpiar listas de agentes
        self.robots.clear()
        self.monsters.clear()
        
        # Crear nuevos robots y monstruos
        print(f"🤖 Creando {NUM_ROBOTS} robots y {NUM_MONSTERS} monstruos...")
        
        for i in range(NUM_ROBOTS):
            if ROBOT_POSITION_MODE == "fixed":
                pos = ROBOT_FIXED_POSITION
                print(f"   Robot {i}: Posición fija {pos}")
            else:
                pos = self.environment.get_random_internal_free_position()
                print(f"   Robot {i}: Posición aleatoria interna {pos}")
            
            if pos:
                robot = Robot(i, pos, self.environment, self.rule_engine)
                self.robots.append(robot)
            else:
                print(f"   ⚠️ No se pudo crear Robot {i}: No hay posiciones libres internas")
        
        for i in range(NUM_MONSTERS):
            if MONSTER_POSITION_MODE == "fixed":
                pos = MONSTER_FIXED_POSITION
                print(f"   Monstruo {i}: Posición fija {pos}")
            else:
                pos = self.environment.get_random_internal_free_position()
                print(f"   Monstruo {i}: Posición aleatoria interna {pos}")
            
            if pos:
                monster = Monster(i, pos, self.environment, self.rule_engine)
                self.monsters.append(monster)
            else:
                print(f"   ⚠️ No se pudo crear Monstruo {i}: No hay posiciones libres internas")
        
        print(f"✅ Simulación reiniciada: {len(self.robots)} robots y {len(self.monsters)} monstruos")
    
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
    
    def cleanup(self):
        """Limpia recursos al cerrar la aplicación"""
        print("\n🧹 Limpiando recursos...")
        self.running = False
        if self.port:
            print(f"🔌 Puerto {self.port} liberado")
    
    def signal_handler(self, signum, frame):
        """Maneja señales de interrupción"""
        print(f"\n🛑 Señal {signum} recibida. Cerrando aplicación...")
        self.cleanup()
        sys.exit(0)
    
    def create_dash_app(self):
        """Crea la aplicación Dash"""
        self.app = dash.Dash(__name__)
        
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
        """Ejecuta la simulación"""
        if not self.initialize_simulation():
            return
        
        print("\n🎬 Configurando aplicación web...")
        self.create_dash_app()
        
        # Encontrar puerto disponible
        self.port = self.find_available_port()
        if not self.port:
            print("❌ Error: No se encontró ningún puerto disponible en el rango 8050-8100")
            return
        
        print("🚀 Iniciando servidor web...")
        print(f"💡 Se abrirá automáticamente en tu navegador en http://127.0.0.1:{self.port}")
        print("💡 Usa los botones para controlar la simulación")
        print("💡 Presiona Ctrl+C para detener el servidor")
        
        # Abrir navegador automáticamente después de un breve delay
        def open_browser():
            time.sleep(2)  # Esperar 2 segundos para que el servidor inicie
            webbrowser.open(f'http://127.0.0.1:{self.port}')
        
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        try:
            self.app.run(debug=False, host='127.0.0.1', port=self.port)
        except KeyboardInterrupt:
            print("\n⏹️ Servidor detenido por el usuario")
        except Exception as e:
            print(f"❌ Error iniciando servidor: {e}")
        finally:
            self.cleanup()

def main():
    """Función principal"""
    simulation = RealTimeSimulation()
    simulation.run()

if __name__ == "__main__":
    main()

