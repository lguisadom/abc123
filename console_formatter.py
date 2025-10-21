#!/usr/bin/env python3
"""
Console Formatter - Sistema mejorado para impresión de consola
Proporciona formato profesional y organizado para la salida de consola
"""

import sys
from typing import Optional, List, Dict, Any
from datetime import datetime

class ConsoleFormatter:
    """Clase para formatear la salida de consola de manera profesional"""
    
    # Colores ANSI
    COLORS = {
        'reset': '\033[0m',
        'bold': '\033[1m',
        'dim': '\033[2m',
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'bg_red': '\033[101m',
        'bg_green': '\033[102m',
        'bg_yellow': '\033[103m',
        'bg_blue': '\033[104m'
    }
    
    def __init__(self, use_colors: bool = True, show_timestamps: bool = False):
        """
        Inicializa el formateador
        
        Args:
            use_colors: Si usar colores en la salida
            show_timestamps: Si mostrar timestamps
        """
        self.use_colors = use_colors and sys.stdout.isatty()
        self.show_timestamps = show_timestamps
        self.section_width = 60
    
    def _colorize(self, text: str, color: str) -> str:
        """Aplica color al texto si está habilitado"""
        if self.use_colors and color in self.COLORS:
            return f"{self.COLORS[color]}{text}{self.COLORS['reset']}"
        return text
    
    def _get_timestamp(self) -> str:
        """Obtiene timestamp actual"""
        if self.show_timestamps:
            return f"[{datetime.now().strftime('%H:%M:%S')}] "
        return ""
    
    def header(self, title: str, char: str = "=") -> None:
        """Imprime un encabezado principal"""
        timestamp = self._get_timestamp()
        colored_title = self._colorize(title, 'bold')
        line = char * self.section_width
        print(f"\n{timestamp}{colored_title}")
        print(f"{timestamp}{line}")
    
    def subheader(self, title: str) -> None:
        """Imprime un subencabezado"""
        timestamp = self._get_timestamp()
        colored_title = self._colorize(title, 'cyan')
        print(f"\n{timestamp}{colored_title}")
        print(f"{timestamp}{'-' * len(title)}")
    
    def info(self, message: str, icon: str = "ℹ️") -> None:
        """Imprime mensaje informativo"""
        timestamp = self._get_timestamp()
        colored_message = self._colorize(f"{icon} {message}", 'blue')
        print(f"{timestamp}{colored_message}")
    
    def success(self, message: str, icon: str = "✅") -> None:
        """Imprime mensaje de éxito"""
        timestamp = self._get_timestamp()
        colored_message = self._colorize(f"{icon} {message}", 'green')
        print(f"{timestamp}{colored_message}")
    
    def warning(self, message: str, icon: str = "⚠️") -> None:
        """Imprime mensaje de advertencia"""
        timestamp = self._get_timestamp()
        colored_message = self._colorize(f"{icon} {message}", 'yellow')
        print(f"{timestamp}{colored_message}")
    
    def error(self, message: str, icon: str = "❌") -> None:
        """Imprime mensaje de error"""
        timestamp = self._get_timestamp()
        colored_message = self._colorize(f"{icon} {message}", 'red')
        print(f"{timestamp}{colored_message}")
    
    def step(self, step_num: int, total_steps: Optional[int] = None) -> None:
        """Imprime información de paso"""
        timestamp = self._get_timestamp()
        if total_steps:
            step_text = f"Paso {step_num}/{total_steps}"
        else:
            step_text = f"Paso {step_num}"
        colored_step = self._colorize(step_text, 'bold')
        print(f"\n{timestamp}{'─' * 20} {colored_step} {'─' * 20}")
    
    def robot_action(self, robot_id: int, action: str, position: tuple, rule_num: Optional[int] = None) -> None:
        """Imprime acción de robot de forma organizada"""
        timestamp = self._get_timestamp()
        robot_header = self._colorize(f"🤖 Robot {robot_id}", 'bold')
        pos_text = f"Pos: {position}"
        
        if rule_num:
            rule_text = self._colorize(f"Regla #{rule_num}", 'dim')
            print(f"{timestamp}{robot_header} | {pos_text} | {rule_text}")
        else:
            print(f"{timestamp}{robot_header} | {pos_text}")
        
        action_text = self._colorize(f"Acción: {action}", 'green')
        print(f"{timestamp}  └─ {action_text}")
    
    def monster_action(self, monster_id: int, action: str, position: tuple, k: int, p: float, steps_remaining: int) -> None:
        """Imprime acción de monstruo de forma organizada"""
        timestamp = self._get_timestamp()
        monster_header = self._colorize(f"👹 Monstruo {monster_id}", 'bold')
        pos_text = f"Pos: {position}"
        params_text = f"K={k}, p={p}, restantes={steps_remaining}"
        
        print(f"{timestamp}{monster_header} | {pos_text} | {params_text}")
        action_text = self._colorize(f"Acción: {action}", 'magenta')
        print(f"{timestamp}  └─ {action_text}")
    
    def stats(self, robots_alive: int, monsters_alive: int, step: int) -> None:
        """Imprime estadísticas del estado actual"""
        timestamp = self._get_timestamp()
        robots_text = self._colorize(f"{robots_alive} robots", 'blue')
        monsters_text = self._colorize(f"{monsters_alive} monstruos", 'red')
        step_text = self._colorize(f"Paso {step}", 'dim')
        
        print(f"{timestamp}📊 Estado: {robots_text} vivos, {monsters_text} vivos | {step_text}")
    
    def sensor_data(self, robot_id: int, sensors: Dict[str, Any], rule_num: Optional[int] = None) -> None:
        """Imprime datos de sensores de forma compacta"""
        timestamp = self._get_timestamp()
        
        # Filtrar sensores importantes
        important_sensors = {k: v for k, v in sensors.items() 
                           if k not in ['Energometro', 'Roboscanner_Front'] and v != 0}
        
        if important_sensors:
            sensor_parts = [f"{k}={v}" for k, v in important_sensors.items()]
            sensor_text = ", ".join(sensor_parts)
            sensor_colored = self._colorize(sensor_text, 'dim')
            
            if rule_num:
                rule_text = self._colorize(f"Regla #{rule_num}", 'dim')
                print(f"{timestamp}  🔍 [{rule_text}, {sensor_colored}]")
            else:
                print(f"{timestamp}  🔍 [{sensor_colored}]")
    
    def list_items(self, items: List[str], title: str, icon: str = "•") -> None:
        """Imprime lista de elementos"""
        timestamp = self._get_timestamp()
        colored_title = self._colorize(title, 'bold')
        print(f"{timestamp}{colored_title}:")
        
        for item in items:
            colored_item = self._colorize(f"  {icon} {item}", 'white')
            print(f"{timestamp}{colored_item}")
    
    def progress_bar(self, current: int, total: int, width: int = 30) -> None:
        """Imprime barra de progreso"""
        timestamp = self._get_timestamp()
        percentage = (current / total) * 100
        filled = int((current / total) * width)
        bar = "█" * filled + "░" * (width - filled)
        
        colored_bar = self._colorize(bar, 'green')
        print(f"{timestamp}Progreso: [{colored_bar}] {percentage:.1f}% ({current}/{total})")
    
    def separator(self, char: str = "─", length: Optional[int] = None) -> None:
        """Imprime separador"""
        timestamp = self._get_timestamp()
        length = length or self.section_width
        print(f"{timestamp}{char * length}")
    
    def clear_screen(self) -> None:
        """Limpia la pantalla"""
        if sys.stdout.isatty():
            print("\033[2J\033[H", end="")

# Instancia global para uso fácil
console = ConsoleFormatter()
