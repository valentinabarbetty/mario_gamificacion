__author__ = 'justinarmstrong'

import pygame as pg
from .. import setup, tools
from .. import constants as c
from .. components import info, mario


class Menu(tools._State):
    def __init__(self):
        """Initializes the state"""
        tools._State.__init__(self)
        persist = {c.COIN_TOTAL: 0,
                   c.SCORE: 0,
                   c.LIVES: 3,
                   c.TOP_SCORE: 0,
                   c.CURRENT_TIME: 0.0,
                   c.LEVEL_STATE: None,
                   c.CAMERA_START_X: 0,
                   c.MARIO_DEAD: False}
        self.startup(0.0, persist)

    def startup(self, current_time, persist):
        """Called every time the game's state becomes this one.  Initializes
        certain values"""
        self.next = c.LOAD_SCREEN
        self.persist = persist
        self.game_info = persist
        self.overhead_info = info.OverheadInfo(self.game_info, c.MAIN_MENU)

        self.sprite_sheet = setup.GFX['title_screen']
        self.setup_background()
        self.setup_mario()
        self.setup_cursor()


    def setup_cursor(self):
        """Creates the mushroom cursor to select 1 or 2 player game"""
        self.cursor = pg.sprite.Sprite()
        dest = (220, 358)
        self.cursor.image, self.cursor.rect = self.get_image(
            24, 160, 8, 8, dest, setup.GFX['item_objects'])
        self.cursor.state = c.PLAYER1


    def setup_mario(self):
        """Places Mario at the beginning of the level"""
        self.mario = mario.Mario()
        self.mario.rect.x = 110
        self.mario.rect.bottom = c.GROUND_HEIGHT


    def setup_background(self):
        """Setup the background image to blit"""
        self.background = setup.GFX['level_1']
        self.background_rect = self.background.get_rect()
        self.background = pg.transform.scale(
            self.background,
            (int(self.background_rect.width * c.BACKGROUND_MULTIPLER),
            int(self.background_rect.height * c.BACKGROUND_MULTIPLER))
        )
        self.viewport = setup.SCREEN.get_rect(bottom=setup.SCREEN_RECT.bottom)

        self.image_dict = {}

        # Fuentes estilo arcade (un poco más grandes)
        self.title_font = pg.font.Font(None, 80)
        self.subtitle_font = pg.font.Font(None, 40)
        self.text_font = pg.font.Font(None, 28)
        self.small_font = pg.font.Font(None, 24)

        # Banner tipo caja de título (estilo Mario, rectángulo oscuro con borde blanco)
        self.banner_rect = pg.Rect(40, 90, 720, 210)

    def get_image(self, x, y, width, height, dest, sprite_sheet):
        """Returns images and rects to blit onto the screen"""
        image = pg.Surface([width, height])
        rect = image.get_rect()

        image.blit(sprite_sheet, (0, 0), (x, y, width, height))
        if sprite_sheet == setup.GFX['title_screen']:
            image.set_colorkey((255, 0, 220))
            image = pg.transform.scale(image,
                                   (int(rect.width*c.SIZE_MULTIPLIER),
                                    int(rect.height*c.SIZE_MULTIPLIER)))
        else:
            image.set_colorkey(c.BLACK)
            image = pg.transform.scale(image,
                                   (int(rect.width*3),
                                    int(rect.height*3)))

        rect = image.get_rect()
        rect.x = dest[0]
        rect.y = dest[1]
        return (image, rect)

    def update(self, surface, keys, current_time):
        """Updates the state every refresh"""
        self.current_time = current_time
        self.game_info[c.CURRENT_TIME] = self.current_time
        self.update_cursor(keys)
        self.overhead_info.update(self.game_info)

        # Fondo original
        surface.blit(self.background, self.viewport, self.viewport)

        # ---------- BANNER PRINCIPAL ----------
        # Caja oscura estilo NES con borde blanco
        pg.draw.rect(surface, (10, 10, 40), self.banner_rect)        # relleno
        pg.draw.rect(surface, c.WHITE, self.banner_rect, 4)          # borde

        center_x = self.banner_rect.centerx

        # ---------- TÍTULO "JUEGOS SERIOS" CON SOMBRA ----------
        title_y = self.banner_rect.y + 30
        # Sombra
        title_shadow = self.title_font.render("JUEGOS SERIOS", True, c.NEAR_BLACK)
        shadow_rect = title_shadow.get_rect(center=(center_x + 4, title_y + 4))
        surface.blit(title_shadow, shadow_rect)

        # Texto principal dorado
        title_text = self.title_font.render("JUEGOS SERIOS", True, c.GOLD)
        title_rect = title_text.get_rect(center=(center_x, title_y))
        surface.blit(title_text, title_rect)

        # ---------- SUBTÍTULO ----------
        subtitle_y = title_rect.bottom + 10
        subtitle_text = self.subtitle_font.render("INTRODUCCIÓN A LA GAMIFICACIÓN", True, c.SKY_BLUE)
        subtitle_rect = subtitle_text.get_rect(center=(center_x, subtitle_y))
        surface.blit(subtitle_text, subtitle_rect)

        # ---------- DETALLES DE CURSO / UNIVERSIDAD ----------
        detail_y = subtitle_rect.bottom + 15
        detail_text = self.text_font.render("Universidad del Valle", True, c.WHITE)
        detail_rect = detail_text.get_rect(center=(center_x, detail_y))
        surface.blit(detail_text, detail_rect)

        detail2_y = detail_rect.bottom + 5
        detail2_text = self.small_font.render("----", True, c.WHITE)
        detail2_rect = detail2_text.get_rect(center=(center_x, detail2_y))
        surface.blit(detail2_text, detail2_rect)

        # ---------- TEXTO PARPADEANTE TIPO 'PRESS START' ----------
        blink_y = self.banner_rect.bottom - 30
        # Parpadeo sencillo cada ~0.4 s (current_time va en milisegundos en este proyecto)
        if (self.current_time // 400) % 2 == 0:
            blink_text = self.small_font.render("PRESIONA A / ENTER PARA EMPEZAR", True, c.GOLD)
            blink_rect = blink_text.get_rect(center=(center_x, blink_y))
            surface.blit(blink_text, blink_rect)

        # ---------- MARIO, CURSOR Y HUD SUPERIOR ----------
        surface.blit(self.mario.image, self.mario.rect)
        surface.blit(self.cursor.image, self.cursor.rect)
        self.overhead_info.draw(surface)

    def update_cursor(self, keys):
        """Update the position of the cursor"""
        input_list = [pg.K_RETURN, pg.K_a, pg.K_s]

        if self.cursor.state == c.PLAYER1:
            self.cursor.rect.y = 358
            if keys[pg.K_DOWN]:
                self.cursor.state = c.PLAYER2
            for input in input_list:
                if keys[input]:
                    self.reset_game_info()
                    self.done = True
        elif self.cursor.state == c.PLAYER2:
            self.cursor.rect.y = 403
            if keys[pg.K_UP]:
                self.cursor.state = c.PLAYER1


    def reset_game_info(self):
        """Resets the game info in case of a Game Over and restart"""
        self.game_info[c.COIN_TOTAL] = 0
        self.game_info[c.SCORE] = 0
        self.game_info[c.LIVES] = 3
        self.game_info[c.CURRENT_TIME] = 0.0
        self.game_info[c.LEVEL_STATE] = None

        self.persist = self.game_info
















