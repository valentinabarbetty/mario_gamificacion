__author__ = 'justinarmstrong'

from .. import setup, tools
from .. import constants as c
from .. import game_sound
from ..components import info


class LoadScreen(tools._State):
    def __init__(self):
        tools._State.__init__(self)

    def startup(self, current_time, persist):
        self.start_time = current_time
        self.persist = persist
        self.game_info = self.persist
        self.next = self.set_next_state()

        info_state = self.set_overhead_info_state()

        self.overhead_info = info.OverheadInfo(self.game_info, info_state)
        self.sound_manager = game_sound.Sound(self.overhead_info)
        
        # Crear fuente para el mensaje de carga
        self.font = setup.pg.font.Font(None, 48)


    def set_next_state(self):
        """Sets the next state"""
        return c.LEVEL1

    def set_overhead_info_state(self):
        """sets the state to send to the overhead info object"""
        return c.LOAD_SCREEN


    def update(self, surface, keys, current_time):
        """Updates the loading screen"""
        if (current_time - self.start_time) < 2400:
            surface.fill(c.BLACK)
            
            # Dibujar mensaje de carga personalizado
            load_text = self.font.render("Preparando Nivel...", True, c.GOLD)
            load_rect = load_text.get_rect(center=(400, 250))
            surface.blit(load_text, load_rect)
            
            # Dibujar un pequeño indicador de progreso
            progress = ((current_time - self.start_time) / 2400.0) * 200
            setup.pg.draw.rect(surface, c.SKY_BLUE, (300, 320, int(progress), 20))
            setup.pg.draw.rect(surface, c.WHITE, (300, 320, 200, 20), 2)
            
            self.overhead_info.update(self.game_info)
            self.overhead_info.draw(surface)

        elif (current_time - self.start_time) < 2600:
            surface.fill(c.BLACK)

        elif (current_time - self.start_time) < 2635:
            surface.fill((106, 150, 252))

        else:
            self.done = True




class GameOver(LoadScreen):
    """A loading screen with Game Over"""
    def __init__(self):
        super(GameOver, self).__init__()


    def set_next_state(self):
        """Sets next state"""
        return c.MAIN_MENU

    def set_overhead_info_state(self):
        """sets the state to send to the overhead info object"""
        return c.GAME_OVER

    def update(self, surface, keys, current_time):
        self.current_time = current_time
        self.sound_manager.update(self.persist, None)

        if (self.current_time - self.start_time) < 7000:
            surface.fill(c.BLACK)
            
            # Mostrar Game Over de forma más visual
            game_over_font = setup.pg.font.Font(None, 96)
            game_over_text = game_over_font.render("GAME OVER", True, c.RED)
            game_over_rect = game_over_text.get_rect(center=(400, 200))
            surface.blit(game_over_text, game_over_rect)
            
            # Mostrar puntuación final
            score_font = setup.pg.font.Font(None, 36)
            score_text = score_font.render(f"Puntuación Final: {self.game_info[c.SCORE]}", True, c.WHITE)
            score_rect = score_text.get_rect(center=(400, 350))
            surface.blit(score_text, score_rect)
            
            self.overhead_info.update(self.game_info)
            self.overhead_info.draw(surface)
        elif (self.current_time - self.start_time) < 7200:
            surface.fill(c.BLACK)
        elif (self.current_time - self.start_time) < 7235:
            surface.fill((106, 150, 252))
        else:
            self.done = True


class TimeOut(LoadScreen):
    """Loading Screen with Time Out"""
    def __init__(self):
        super(TimeOut, self).__init__()

    def set_next_state(self):
        """Sets next state"""
        if self.persist[c.LIVES] == 0:
            return c.GAME_OVER
        else:
            return c.LOAD_SCREEN

    def set_overhead_info_state(self):
        """Sets the state to send to the overhead info object"""
        return c.TIME_OUT

    def update(self, surface, keys, current_time):
        self.current_time = current_time

        if (self.current_time - self.start_time) < 2400:
            surface.fill(c.BLACK)
            self.overhead_info.update(self.game_info)
            self.overhead_info.draw(surface)
        else:
            self.done = True









