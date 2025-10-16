#!/usr/bin/env python3
"""
Módulo Environment - Entorno 3D de la simulación
Contiene la clase Environment que maneja el mundo 3D
"""

import numpy as np
import plotly.graph_objects as go
import random
from typing import List, Tuple, Optional
from config import WORLD_SIZE, PERCENTAGE_FREE, PERCENTAGE_EMPTY, CUBE_SIZE, FIGURE_WIDTH, FIGURE_HEIGHT, MONSTER_VISUALIZATION, MONSTER_SIZE_PERCENTAGE, INTERNAL_EMPTY_RATIO, FREE_ZONE_OPACITY, MONSTER_OPACITY, MONSTER_SHADOW_OPACITY, BORDER_OPACITY, MONSTER_CENTER_OFFSET

class Environment:
    """
    Entorno 3D conformado por N³ cubos (hexaedro regular)
    Contiene zonas libres (0) y zonas vacías (-1)
    """
    
    def __init__(self, N: int = None, Pfree: float = None, Psoft: float = None):
        """
        Inicializa el entorno 3D
        
        Args:
            N: Tamaño del lado del cubo (mundo NxNxN). Si es None, usa WORLD_SIZE
            Pfree: Porcentaje de zonas libres. Si es None, usa PERCENTAGE_FREE
            Psoft: Porcentaje de zonas vacías. Si es None, usa PERCENTAGE_EMPTY
        """
        self.N = N if N is not None else WORLD_SIZE
        self.Pfree = Pfree if Pfree is not None else PERCENTAGE_FREE
        self.Psoft = Psoft if Psoft is not None else PERCENTAGE_EMPTY
        
        # Crear el mundo 3D
        self.world = np.zeros((self.N, self.N, self.N), dtype=int)
        self._generate_world()
        
        # Parámetros de visualización
        self.cube_size = CUBE_SIZE
        self.world_size = self.N * self.cube_size
        
        # Registro de agentes para detección real
        self.robot_positions = {}  # {robot_id: (x, y, z)}
        self.monster_positions = {}  # {monster_id: (x, y, z)}
        
    def _generate_world(self):
        """Genera el mundo aleatoriamente según los parámetros"""
        total_cells = self.N ** 3
        
        # Calcular número de zonas vacías INTERNAS (no fronteras)
        # Reducir significativamente el porcentaje para garantizar posiciones libres
        internal_cells = (self.N - 2) ** 3 if self.N > 2 else 0
        num_internal_empty = int(internal_cells * (self.Psoft * INTERNAL_EMPTY_RATIO * 0.5))  # Reducir a la mitad
        
        # Crear lista de posiciones INTERNAS (no fronteras)
        internal_positions = [(x, y, z) for x in range(1, self.N-1) 
                             for y in range(1, self.N-1) 
                             for z in range(1, self.N-1)]
        
        # Seleccionar posiciones aleatorias para zonas vacías internas
        if internal_positions and num_internal_empty > 0:
            empty_internal_positions = random.sample(internal_positions, 
                                                   min(num_internal_empty, len(internal_positions)))
            
            # Marcar zonas vacías internas
            for pos in empty_internal_positions:
                self.world[pos] = -1
        
        # Las zonas libres quedan como 0 (valor por defecto)
        
        # Crear fronteras invisibles (sin color, solo límites)
        self._create_boundaries()
    
    def _create_boundaries(self):
        """Crea fronteras como zonas vacías alrededor del mundo"""
        for x in range(self.N):
            for y in range(self.N):
                for z in range(self.N):
                    # Si está en el borde, marcar como zona vacía
                    if (x == 0 or x == self.N-1 or 
                        y == 0 or y == self.N-1 or 
                        z == 0 or z == self.N-1):
                        self.world[x, y, z] = -1  # -1 = zona vacía (borde del mundo)
    
    def is_valid_position(self, x: int, y: int, z: int) -> bool:
        """Verifica si una posición es válida (zona libre)"""
        if (x < 0 or x >= self.N or 
            y < 0 or y >= self.N or 
            z < 0 or z >= self.N):
            return False
        # Solo las zonas libres (0) son válidas, las zonas vacías (-1) y fronteras (-2) no
        return self.world[x, y, z] == 0
    
    def get_free_positions(self) -> List[Tuple[int, int, int]]:
        """Obtiene todas las posiciones libres disponibles"""
        free_positions = []
        for x in range(self.N):
            for y in range(self.N):
                for z in range(self.N):
                    if self.world[x, y, z] == 0:
                        free_positions.append((x, y, z))
        return free_positions
    
    def get_internal_free_positions(self) -> List[Tuple[int, int, int]]:
        """Obtiene todas las posiciones libres internas (no fronteras)"""
        free_positions = []
        for x in range(1, self.N-1):
            for y in range(1, self.N-1):
                for z in range(1, self.N-1):
                    if self.world[x, y, z] == 0:
                        free_positions.append((x, y, z))
        return free_positions
    
    def get_random_internal_free_position(self) -> Optional[Tuple[int, int, int]]:
        """
        Obtiene una posición aleatoria libre interna (no fronteras)
        
        Returns:
            Tuple[int, int, int] o None si no hay posiciones libres internas
        """
        free_positions = self.get_internal_free_positions()
        if free_positions:
            return random.choice(free_positions)
        return None
    
    def is_monster_at(self, position: Tuple[int, int, int]) -> bool:
        """
        Verifica si hay un monstruo en la posición dada
        
        Args:
            position: Posición a verificar
            
        Returns:
            bool: True si hay un monstruo
        """
        x, y, z = position
        if not (0 <= x < self.N and 0 <= y < self.N and 0 <= z < self.N):
            return False
        
        # Verificar en el registro de posiciones de monstruos
        return position in self.monster_positions.values()
    
    def is_empty_at(self, position: Tuple[int, int, int]) -> bool:
        """
        Verifica si hay una zona vacía en la posición dada
        
        Args:
            position: Posición a verificar
            
        Returns:
            bool: True si es una zona vacía
        """
        x, y, z = position
        if not (0 <= x < self.N and 0 <= y < self.N and 0 <= z < self.N):
            return True  # Fuera del mundo es considerado vacío
        
        return self.world[x, y, z] == -1  # -1 = zona vacía (incluye bordes)
    
    def is_robot_at(self, position: Tuple[int, int, int], exclude_id: int = None) -> bool:
        """
        Verifica si hay un robot en la posición dada
        
        Args:
            position: Posición a verificar
            exclude_id: ID del robot a excluir de la búsqueda
            
        Returns:
            bool: True si hay un robot
        """
        x, y, z = position
        if not (0 <= x < self.N and 0 <= y < self.N and 0 <= z < self.N):
            return False
        
        # Verificar en el registro de posiciones de robots
        for robot_id, robot_pos in self.robot_positions.items():
            if robot_pos == position and (exclude_id is None or robot_id != exclude_id):
                return True
        return False
    
    def remove_monster_at(self, position: Tuple[int, int, int]):
        """
        Remueve un monstruo de la posición dada
        
        Args:
            position: Posición del monstruo a remover
        """
        # Remover del registro de posiciones
        for monster_id, monster_pos in list(self.monster_positions.items()):
            if monster_pos == position:
                del self.monster_positions[monster_id]
                break
    
    def create_empty_zone_at(self, position: Tuple[int, int, int]):
        """
        Crea una zona vacía en la posición dada
        
        Args:
            position: Posición donde crear la zona vacía
        """
        x, y, z = position
        if (0 <= x < self.N and 0 <= y < self.N and 0 <= z < self.N):
            self.world[x, y, z] = -1  # -1 = zona vacía
            print(f"Zona vacía creada en {position}")
    
    def register_robot(self, robot_id: int, position: Tuple[int, int, int]):
        """
        Registra la posición de un robot
        
        Args:
            robot_id: ID del robot
            position: Posición del robot
        """
        self.robot_positions[robot_id] = position
    
    def register_monster(self, monster_id: int, position: Tuple[int, int, int]):
        """
        Registra la posición de un monstruo
        
        Args:
            monster_id: ID del monstruo
            position: Posición del monstruo
        """
        self.monster_positions[monster_id] = position
    
    def update_robot_position(self, robot_id: int, old_position: Tuple[int, int, int], new_position: Tuple[int, int, int]):
        """
        Actualiza la posición de un robot
        
        Args:
            robot_id: ID del robot
            old_position: Posición anterior
            new_position: Nueva posición
        """
        if robot_id in self.robot_positions:
            self.robot_positions[robot_id] = new_position
    
    def update_monster_position(self, monster_id: int, old_position: Tuple[int, int, int], new_position: Tuple[int, int, int]):
        """
        Actualiza la posición de un monstruo
        
        Args:
            monster_id: ID del monstruo
            old_position: Posición anterior
            new_position: Nueva posición
        """
        if monster_id in self.monster_positions:
            self.monster_positions[monster_id] = new_position
    
    def unregister_robot(self, robot_id: int):
        """
        Desregistra un robot del entorno
        
        Args:
            robot_id: ID del robot a desregistrar
        """
        if robot_id in self.robot_positions:
            del self.robot_positions[robot_id]
    
    
    def visualize(self, robots: List = None, monsters: List = None):
        """
        Crea visualización 3D del entorno usando Plotly
        
        Args:
            robots: Lista de robots para visualizar
            monsters: Lista de monstruos para visualizar
        """
        fig = go.Figure()
        
        # Crear cubos del entorno
        self._add_environment_cubes(fig)
        
        # Agregar robots si existen
        if robots:
            self._add_robots(fig, robots)
            
        # Agregar monstruos si existen
        if monsters:
            self._add_monsters(fig, monsters)
        
        # Calcular estadísticas para la leyenda
        stats = self._calculate_environment_stats(robots, monsters)
        
        # Configurar la escena
        fig.update_layout(
            title=f"🤖 Simulación Robots Monstruicidas vs Monstruos<br><sub>Robots: {stats['robots_alive']} | Monstruos: {stats['monsters_alive']} | Libres: {stats['free_zones']} | Vacías Internas: {stats['empty_zones']} | Bordes: {stats['boundary_zones']}</sub>",
            scene=dict(
                xaxis=dict(range=[0, self.N], title="X", dtick=1),  # Cada unidad = 1 cubo
                yaxis=dict(range=[0, self.N], title="Y", dtick=1),  # Cada unidad = 1 cubo
                zaxis=dict(range=[0, self.N], title="Z", dtick=1),  # Cada unidad = 1 cubo
                aspectmode="cube",
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.5)
                )
            ),
            width=FIGURE_WIDTH,
            height=FIGURE_HEIGHT,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=1.01,
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor=f"rgba(0,0,0,{BORDER_OPACITY})",
                borderwidth=1
            )
        )
        
        return fig
    
    def _calculate_environment_stats(self, robots=None, monsters=None):
        """
        Calcula estadísticas del entorno para mostrar en la leyenda
        
        Args:
            robots: Lista de robots
            monsters: Lista de monstruos
            
        Returns:
            Dict con estadísticas del entorno
        """
        stats = {
            'robots_alive': 0,
            'monsters_alive': 0,
            'free_zones': 0,
            'empty_zones': 0,
            'boundary_zones': 0
        }
        
        # Contar robots vivos
        if robots:
            stats['robots_alive'] = sum(1 for robot in robots if robot.alive)
        
        # Contar monstruos vivos
        if monsters:
            stats['monsters_alive'] = sum(1 for monster in monsters if monster.alive)
        
        # Contar zonas del entorno
        for x in range(self.N):
            for y in range(self.N):
                for z in range(self.N):
                    cell_value = self.world[x, y, z]
                    if cell_value == 0:
                        stats['free_zones'] += 1
                    elif cell_value == -1:
                        # Distinguir entre zonas vacías internas y del borde
                        is_boundary = (x == 0 or x == self.N-1 or 
                                     y == 0 or y == self.N-1 or 
                                     z == 0 or z == self.N-1)
                        if is_boundary:
                            stats['boundary_zones'] += 1
                        else:
                            stats['empty_zones'] += 1
                    elif cell_value == -2:
                        stats['boundary_zones'] += 1
        
        return stats
    
    def _add_environment_cubes(self, fig):
        """Agrega los cubos del entorno a la visualización usando cubos reales"""
        # Usar enfoque denso para mundos pequeños (como nuestro 5x5x5)
        self._add_environment_dense(fig)
    
    def _add_environment_dense(self, fig):
        """Agrega cubos individuales usando un enfoque de cubos 3D reales"""
        # Crear cubos 3D reales para zonas libres
        self._add_cube_cluster(fig, 'free', 'lightgreen', FREE_ZONE_OPACITY)
        
        # Crear cubos 3D reales para zonas vacías internas
        self._add_cube_cluster(fig, 'empty', 'red', 0.4)
        
        # Agregar grilla 3D para delimitar cubos
        self._add_3d_grid(fig)
        
        # NO agregar envoltorio exterior - dejar invisible para mejor visualización
    
    def _add_cube_cluster(self, fig, zone_type, color, opacity):
        """Crea un cluster de cubos 3D reales usando Mesh3d"""
        # Preparar vértices y caras para todos los cubos del tipo especificado
        vertices_x, vertices_y, vertices_z = [], [], []
        faces = []
        vertex_offset = 0
        
        for x in range(self.N):
            for y in range(self.N):
                for z in range(self.N):
                    # Para zonas libres: mostrar todas
                    if zone_type == 'free' and self.world[x, y, z] == 0:
                        # Crear vértices del cubo (8 vértices)
                        cube_vertices = self._get_cube_vertices(x, y, z)
                        vertices_x.extend(cube_vertices[0])
                        vertices_y.extend(cube_vertices[1])
                        vertices_z.extend(cube_vertices[2])
                        
                        # Crear caras del cubo (12 triángulos = 6 caras × 2 triángulos)
                        cube_faces = self._get_cube_faces(vertex_offset)
                        faces.extend(cube_faces)
                        
                        vertex_offset += 8
                    
                    # Para zonas vacías: solo mostrar las internas (no bordes)
                    elif zone_type == 'empty' and self.world[x, y, z] == -1:
                        # Verificar si es una zona vacía interna (no borde)
                        is_boundary = (x == 0 or x == self.N-1 or 
                                     y == 0 or y == self.N-1 or 
                                     z == 0 or z == self.N-1)
                        
                        # Solo mostrar si NO es borde
                        if not is_boundary:
                            # Crear vértices del cubo (8 vértices)
                            cube_vertices = self._get_cube_vertices(x, y, z)
                            vertices_x.extend(cube_vertices[0])
                            vertices_y.extend(cube_vertices[1])
                            vertices_z.extend(cube_vertices[2])
                            
                            # Crear caras del cubo (12 triángulos = 6 caras × 2 triángulos)
                            cube_faces = self._get_cube_faces(vertex_offset)
                            faces.extend(cube_faces)
                            
                            vertex_offset += 8
        
        # Solo agregar si hay cubos de este tipo
        if vertices_x:
            fig.add_trace(go.Mesh3d(
                x=vertices_x, y=vertices_y, z=vertices_z,
                i=[face[0] for face in faces],
                j=[face[1] for face in faces],
                k=[face[2] for face in faces],
                color=color,
                opacity=opacity,
                name=f'Zonas {"Libres" if zone_type == "free" else "Vacías Internas"} ({len(vertices_x)//8})',
                hovertemplate=f'<b>Zona {"Libre" if zone_type == "free" else "Vacía Interna"}</b><extra></extra>'
            ))
    
    def _get_cube_vertices(self, x, y, z):
        """Obtiene los 8 vértices de un cubo en la posición (x,y,z)"""
        # Los vértices van de (x,y,z) a (x+1,y+1,z+1)
        vertices_x = [x, x+1, x+1, x,   x, x+1, x+1, x]
        vertices_y = [y, y,   y+1, y+1, y, y,   y+1, y+1]
        vertices_z = [z, z,   z,   z,   z+1, z+1, z+1, z+1]
        return [vertices_x, vertices_y, vertices_z]
    
    def _get_cube_faces(self, vertex_offset):
        """Obtiene las 12 caras triangulares de un cubo"""
        # Cada cara del cubo se divide en 2 triángulos
        # Los índices se ajustan por el offset de vértices
        base_faces = [
            # Cara frontal (z=0)
            [0, 1, 2], [0, 2, 3],
            # Cara trasera (z=1)
            [4, 7, 6], [4, 6, 5],
            # Cara izquierda (x=0)
            [0, 3, 7], [0, 7, 4],
            # Cara derecha (x=1)
            [1, 5, 6], [1, 6, 2],
            # Cara inferior (y=0)
            [0, 4, 5], [0, 5, 1],
            # Cara superior (y=1)
            [2, 6, 7], [2, 7, 3]
        ]
        
        # Ajustar índices por el offset
        return [[face[0] + vertex_offset, face[1] + vertex_offset, face[2] + vertex_offset] 
                for face in base_faces]
    
    def _add_3d_grid(self, fig):
        """Agrega bordes grises alrededor de cada cubo individual (excepto bordes del mundo)"""
        # Crear bordes para cada cubo que existe
        for x in range(self.N):
            for y in range(self.N):
                for z in range(self.N):
                    # Solo agregar bordes si hay un cubo en esta posición Y no es borde del mundo
                    if self.world[x, y, z] in [0, -1]:  # Zona libre o vacía
                        # Verificar si es una zona del borde del mundo
                        is_boundary = (x == 0 or x == self.N-1 or 
                                     y == 0 or y == self.N-1 or 
                                     z == 0 or z == self.N-1)
                        
                        # Solo agregar bordes si NO es borde del mundo
                        if not is_boundary:
                            self._add_cube_borders(fig, x, y, z)
    
    def _add_cube_borders(self, fig, x, y, z):
        """Agrega bordes grises alrededor de un cubo específico"""
        # Definir los 12 bordes del cubo (4 por cada cara)
        edges = [
            # Cara frontal (z = z)
            [[x, x+1], [y, y], [z, z]],      # Borde inferior
            [[x+1, x+1], [y, y+1], [z, z]],  # Borde derecho
            [[x, x+1], [y+1, y+1], [z, z]], # Borde superior
            [[x, x], [y, y+1], [z, z]],      # Borde izquierdo
            
            # Cara trasera (z = z+1)
            [[x, x+1], [y, y], [z+1, z+1]],      # Borde inferior
            [[x+1, x+1], [y, y+1], [z+1, z+1]],  # Borde derecho
            [[x, x+1], [y+1, y+1], [z+1, z+1]], # Borde superior
            [[x, x], [y, y+1], [z+1, z+1]],      # Borde izquierdo
            
            # Bordes verticales (conectando caras frontal y trasera)
            [[x, x], [y, y], [z, z+1]],      # Borde frontal-inferior-izquierdo
            [[x+1, x+1], [y, y], [z, z+1]],  # Borde frontal-inferior-derecho
            [[x, x], [y+1, y+1], [z, z+1]],  # Borde frontal-superior-izquierdo
            [[x+1, x+1], [y+1, y+1], [z, z+1]] # Borde frontal-superior-derecho
        ]
        
        # Agregar cada borde como una línea
        for edge in edges:
            fig.add_trace(go.Scatter3d(
                x=edge[0], y=edge[1], z=edge[2],
                mode='lines',
                line=dict(
                    color='gray',
                    width=2
                ),
                showlegend=False,
                hoverinfo='skip'
            ))
    
    
    def _add_robots(self, fig, robots):
        """Agrega robots a la visualización como cubos sólidos con flecha de orientación"""
        if not robots:
            return
            
        robot_data = []
        robots_alive = sum(1 for robot in robots if robot.alive)
        
        for robot in robots:
            if robot.alive:
                x, y, z = robot.position
                orientation = robot.orientation
                robot_data.append((x, y, z, orientation))
        
        # Solo agregar si hay robots vivos
        if robot_data:
            # Crear cubos sólidos para cada robot
            for x, y, z, orientation in robot_data:
                # Crear un cubo sólido para el robot
                vertices = self._get_cube_vertices(x, y, z)
                faces = self._get_cube_faces(0)  # Offset 0 para cada robot individual
                
                fig.add_trace(go.Mesh3d(
                    x=vertices[0],
                    y=vertices[1], 
                    z=vertices[2],
                    i=[face[0] for face in faces],
                    j=[face[1] for face in faces],
                    k=[face[2] for face in faces],
                    color='cyan',
                    opacity=0.8,  # Semi-transparente para distinguir del entorno
                    name=f'Robots ({robots_alive})',
                    hovertemplate=f'<b>Robot</b><br>Pos: ({x}, {y}, {z})<br>Orientación: {orientation}<extra></extra>',
                    showlegend=False  # Solo mostrar una entrada en la leyenda
                ))
                
                # Agregar flecha de orientación
                self._add_robot_arrow(fig, x, y, z, orientation)
            
            # Agregar una entrada en la leyenda para todos los robots
            fig.add_trace(go.Scatter3d(
                x=[], y=[], z=[],
                mode='markers',
                marker=dict(color='cyan', size=10, symbol='square'),
                name=f'Robots ({robots_alive})',
                showlegend=True,
                hovertemplate='<extra></extra>'
            ))
    
    def _add_robot_arrow(self, fig, x, y, z, orientation):
        """Agrega una flecha que muestra la orientación del robot"""
        # Centro del cubo del robot
        center_x = x + 0.5
        center_y = y + 0.5
        center_z = z + 0.5
        
        # Calcular la dirección de la flecha basada en la orientación
        ox, oy, oz = orientation
        
        # Longitud de la flecha (desde el centro hacia el borde del cubo)
        arrow_length = 0.6  # Aumentar longitud de la flecha
        
        # Posición final de la flecha
        end_x = center_x + (ox * arrow_length)
        end_y = center_y + (oy * arrow_length)
        end_z = center_z + (oz * arrow_length)
        
        # Crear la flecha usando una línea con marcador de flecha
        fig.add_trace(go.Scatter3d(
            x=[center_x, end_x],
            y=[center_y, end_y],
            z=[center_z, end_z],
            mode='lines+markers',
            line=dict(color='red', width=8),  # Línea más gruesa
            marker=dict(
                size=[0, 15],  # Marcador más grande en el final
                color='red',
                symbol=['circle', 'circle'],
                line=dict(width=3, color='darkred')
            ),
            name='Orientación Robot',
            showlegend=False,
            hovertemplate=f'<b>Dirección Robot</b><br>Hacia: ({ox}, {oy}, {oz})<extra></extra>'
        ))
    
    def _add_monsters(self, fig, monsters):
        """Agrega monstruos a la visualización con diferentes opciones según configuración"""
        if not monsters:
            return
        
        # Filtrar monstruos vivos
        alive_monsters = [m for m in monsters if m.alive]
        if not alive_monsters:
            return
        
        # Aplicar visualización según configuración
        if MONSTER_VISUALIZATION == "cloud":
            self._add_monsters_as_cloud(fig, alive_monsters)
        elif MONSTER_VISUALIZATION == "mist":
            self._add_monsters_as_mist(fig, alive_monsters)
        elif MONSTER_VISUALIZATION == "energy":
            self._add_monsters_as_energy(fig, alive_monsters)
        elif MONSTER_VISUALIZATION == "void":
            self._add_monsters_as_void(fig, alive_monsters)
        elif MONSTER_VISUALIZATION == "shadow":
            self._add_monsters_as_shadow(fig, alive_monsters)
        else:
            # Por defecto, usar cloud
            self._add_monsters_as_cloud(fig, alive_monsters)
    
    def _add_monsters_as_cloud(self, fig, monsters):
        """Monstruos como nubes rojas difusas que ocupan el cubo completo"""
        monster_x, monster_y, monster_z = [], [], []
        
        for monster in monsters:
            x, y, z = monster.position
            # Posicionar en el centro del cubo
            monster_x.append(x + MONSTER_CENTER_OFFSET)
            monster_y.append(y + MONSTER_CENTER_OFFSET)
            monster_z.append(z + MONSTER_CENTER_OFFSET)
        
        # Calcular tamaño basado en el porcentaje del cubo
        monster_size = 80 * MONSTER_SIZE_PERCENTAGE  # Base de 80, escalado por porcentaje
        
        fig.add_trace(go.Scatter3d(
            x=monster_x, y=monster_y, z=monster_z,
            mode='markers',
            marker=dict(
                size=monster_size,  # Tamaño configurable basado en porcentaje del cubo
                color='red',
                opacity=0.6,  # Semi-transparente como nube
                symbol='circle',
                line=dict(
                    color='darkred',
                    width=1  # Borde más delgado
                ),
                sizemode='diameter',  # Usar diámetro en lugar de área
                sizeref=1  # Referencia de tamaño
            ),
            name=f'Monstruos ({len(monsters)})',
            hovertemplate='<b>Monstruo</b><br>Pos: (%{x:.0f}, %{y:.0f}, %{z:.0f})<extra></extra>'
        ))
    
    def _add_monsters_as_mist(self, fig, monsters):
        """Monstruos como niebla púrpura que ocupa el cubo completo"""
        monster_x, monster_y, monster_z = [], [], []
        
        for monster in monsters:
            x, y, z = monster.position
            monster_x.append(x + MONSTER_CENTER_OFFSET)
            monster_y.append(y + MONSTER_CENTER_OFFSET)
            monster_z.append(z + MONSTER_CENTER_OFFSET)
        
        # Calcular tamaño basado en el porcentaje del cubo
        monster_size = 80 * MONSTER_SIZE_PERCENTAGE  # Base de 80, escalado por porcentaje
        
        fig.add_trace(go.Scatter3d(
            x=monster_x, y=monster_y, z=monster_z,
            mode='markers',
            marker=dict(
                size=monster_size,  # Tamaño configurable basado en porcentaje del cubo
                color='purple',
                opacity=0.4,  # Muy transparente como niebla
                symbol='circle',
                line=dict(
                    color='darkmagenta',
                    width=0.5
                ),
                sizemode='diameter',  # Usar diámetro en lugar de área
                sizeref=1  # Referencia de tamaño
            ),
            name=f'Monstruos ({len(monsters)})',
            hovertemplate='<b>Monstruo</b><br>Pos: (%{x:.0f}, %{y:.0f}, %{z:.0f})<extra></extra>'
        ))
    
    def _add_monsters_as_energy(self, fig, monsters):
        """Monstruos como energía eléctrica amarilla que ocupa el cubo completo"""
        monster_x, monster_y, monster_z = [], [], []
        
        for monster in monsters:
            x, y, z = monster.position
            monster_x.append(x + MONSTER_CENTER_OFFSET)
            monster_y.append(y + MONSTER_CENTER_OFFSET)
            monster_z.append(z + MONSTER_CENTER_OFFSET)
        
        fig.add_trace(go.Scatter3d(
            x=monster_x, y=monster_y, z=monster_z,
            mode='markers',
            marker=dict(
                size=22,
                color='yellow',
                opacity=MONSTER_OPACITY,
                symbol='diamond',  # Forma de diamante para energía
                line=dict(
                    color='orange',
                    width=2
                )
            ),
            name=f'Monstruos ({len(monsters)})',
            hovertemplate='<b>Monstruo</b><br>Pos: (%{x:.0f}, %{y:.0f}, %{z:.0f})<extra></extra>'
        ))
    
    def _add_monsters_as_void(self, fig, monsters):
        """Monstruos como vacío negro que ocupa el cubo completo"""
        monster_x, monster_y, monster_z = [], [], []
        
        for monster in monsters:
            x, y, z = monster.position
            monster_x.append(x + MONSTER_CENTER_OFFSET)
            monster_y.append(y + MONSTER_CENTER_OFFSET)
            monster_z.append(z + MONSTER_CENTER_OFFSET)
        
        fig.add_trace(go.Scatter3d(
            x=monster_x, y=monster_y, z=monster_z,
            mode='markers',
            marker=dict(
                size=28,
                color='black',
                opacity=0.8,
                symbol='square',  # Forma cuadrada para vacío
                line=dict(
                    color='gray',
                    width=1
                )
            ),
            name=f'Monstruos ({len(monsters)})',
            hovertemplate='<b>Monstruo</b><br>Pos: (%{x:.0f}, %{y:.0f}, %{z:.0f})<extra></extra>'
        ))
    
    def _add_monsters_as_shadow(self, fig, monsters):
        """Monstruos como sombras grises que ocupan el cubo completo"""
        monster_x, monster_y, monster_z = [], [], []
        
        for monster in monsters:
            x, y, z = monster.position
            monster_x.append(x + MONSTER_CENTER_OFFSET)
            monster_y.append(y + MONSTER_CENTER_OFFSET)
            monster_z.append(z + MONSTER_CENTER_OFFSET)
        
        fig.add_trace(go.Scatter3d(
            x=monster_x, y=monster_y, z=monster_z,
            mode='markers',
            marker=dict(
                size=24,
                color='gray',
                opacity=MONSTER_SHADOW_OPACITY,
                symbol='circle',
                line=dict(
                    color='darkgray',
                    width=1
                )
            ),
            name=f'Monstruos ({len(monsters)})',
            hovertemplate='<b>Monstruo</b><br>Pos: (%{x:.0f}, %{y:.0f}, %{z:.0f})<extra></extra>'
        ))
