import pygame as pg

class PopupText:
    def __init__(self):
        self.active = False
        self.image = None
        self.width = 800
        self.height = 500

    def show(self, image_path):
        print(f"📸 Cargando diapositiva: {image_path}")
        self.image = pg.image.load(image_path).convert_alpha()
        self.image = pg.transform.scale(self.image, (self.width, self.height))
        self.active = True

    def hide(self):
        self.active = False

    def draw(self, surface):
        if not self.active:
            return

        sw, sh = surface.get_size()

        # Fondo oscuro
        overlay = pg.Surface((sw, sh), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        # Centrar imagen
        rect = self.image.get_rect(center=(sw // 2, sh // 2))
        surface.blit(self.image, rect)

        # Texto instrucción
        font = pg.font.SysFont("Arial", 26, bold=True)
        text = font.render("Presiona X para continuar", True, (255, 255, 255))
        trect = text.get_rect(center=(sw // 2, sh - 60))
        surface.blit(text, trect)
