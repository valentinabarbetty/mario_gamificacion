import pygame as pg
from .. import setup
from .. import constants as c


class PopupText:
    """Muestra una diapositiva como un cuadro de diálogo amigable.

    Cambios principales:
    - Dibuja un fondo semitransparente pero solo un cuadro centrado (no ocupa toda la pantalla).
    - Añade borde redondeado y texto de instrucción dentro del cuadro.
    - Animación simple de entrada (slide + fade).
    """

    def __init__(self):
        self.active = False
        self.image = None

        # Tamaño del diálogo (ajustable)
        self.dialog_w = 700
        self.dialog_h = 360
        self.padding = 16
        self.border_radius = 12

        # Animación de entrada
        self._anim_progress = 0.0  # 0..1
        self._anim_speed = 0.12

        # Superficies y fuentes cacheadas
        self._dialog_surf = None
        self._font = None
        # Cargar iconos decorativos desde el sprite sheet
        self._icons = []
        try:
            self._icons.append(self._get_icon(52, 113, 8, 14))  # moneda
            self._icons.append(self._get_icon(1, 48, 15, 16))   # estrella
            self._icons.append(self._get_icon(68, 20, 8, 8))    # trozo de ladrillo
            self._icons.append(self._get_icon(0, 32, 16, 16))   # flor (fireflower)
        except Exception:
            # Si falla (por ejemplo en tests sin resources), dejar lista vacía
            self._icons = []


    def show(self, image_path):
        print(f"📸 Cargando diapositiva: {image_path}")
        self.image = pg.image.load(image_path).convert_alpha()
        # Escalar la imagen para que quepa dentro del contenido del diálogo
        max_w = self.dialog_w - (self.padding * 2)
        max_h = self.dialog_h - (self.padding * 2) - 40  # dejar espacio para texto
        iw, ih = self.image.get_size()
        scale = min(max_w / iw, max_h / ih, 1)
        new_size = (max(1, int(iw * scale)), max(1, int(ih * scale)))
        self.image = pg.transform.smoothscale(self.image, new_size)

        self.active = True
        self._anim_progress = 0.0

        if not self._font:
            self._font = pg.font.SysFont("Arial", 20, bold=True)

    def _get_icon(self, x, y, width, height):
        """Extrae y escala un icono pequeño desde el sprite sheet `item_objects`."""
        sprite_sheet = setup.GFX.get('item_objects')
        if sprite_sheet is None:
            raise RuntimeError('No se encontró item_objects en GFX')

        image = pg.Surface([width, height]).convert()
        rect = image.get_rect()
        image.blit(sprite_sheet, (0, 0), (x, y, width, height))
        image.set_colorkey(c.BLACK)
        image = pg.transform.scale(image,
                                   (int(rect.width * c.SIZE_MULTIPLIER),
                                    int(rect.height * c.SIZE_MULTIPLIER)))
        return image

    def _draw_decorative_frame(self, dialog):
        """Dibuja líneas y acentos dentro del diálogo para un marco con estilo del juego.

        Usa colores y un patrón de guiones/píxeles para que haga juego con el resto.
        """
        w, h = self.dialog_w, self.dialog_h

        # Colores (usar constantes del juego cuando estén disponibles)
        accent = getattr(c, 'GOLD', (255, 215, 0))
        dark = getattr(c, 'NEAR_BLACK', (19, 15, 48))
        com = getattr(c, 'COMBLUE', (233, 232, 255))

        # Dibujar un acento exterior delgado un poco adentro del borde
        outer_inset = 8
        try:
            pg.draw.rect(dialog, accent, (outer_inset, outer_inset, w - outer_inset * 2, h - outer_inset * 2), width=2, border_radius=max(0, self.border_radius - 4))
        except Exception:
            # fallback si la versión de pygame no soporta border_radius en rect draw
            pg.draw.rect(dialog, accent, (outer_inset, outer_inset, w - outer_inset * 2, h - outer_inset * 2), width=2)

        # Dibujar guiones (pixel style) en los bordes superiores e inferiores
        dash_color = dark
        dash_w = 6
        gap = 10
        y_top = outer_inset + 6
        y_bottom = h - outer_inset - 6
        for x in range(outer_inset + 6, w - outer_inset - 6, dash_w + gap):
            pg.draw.rect(dialog, dash_color, (x, y_top, dash_w, 3))
            pg.draw.rect(dialog, dash_color, (x, y_bottom, dash_w, 3))

        # Dibujar guiones verticales en los laterales
        x_left = outer_inset + 6
        x_right = w - outer_inset - 6
        for y in range(outer_inset + 20, h - outer_inset - 20, dash_w + gap):
            pg.draw.rect(dialog, dash_color, (x_left, y, 3, dash_w))
            pg.draw.rect(dialog, dash_color, (x_right, y, 3, dash_w))

        # Pequeño header/etiqueta en la parte superior (barra suave)
        header_h = 28
        header_rect = (outer_inset + 12, outer_inset + 6, w - (outer_inset + 12) * 2, header_h)
        try:
            pg.draw.rect(dialog, com, header_rect, border_radius=6)
        except Exception:
            pg.draw.rect(dialog, com, header_rect)

        # Dibujar dos líneas finas sobre y bajo la cabecera para dar profundidad
        pg.draw.line(dialog, (220, 220, 220), (header_rect[0] + 6, header_rect[1] + 4), (header_rect[0] + header_rect[2] - 6, header_rect[1] + 4), 2)
        pg.draw.line(dialog, (200, 200, 200), (header_rect[0] + 6, header_rect[1] + header_rect[3] - 4), (header_rect[0] + header_rect[2] - 6, header_rect[1] + header_rect[3] - 4), 2)

    def hide(self):
        self.active = False

    def draw(self, surface):
        if not self.active:
            return

        sw, sh = surface.get_size()

        # Fondo de atenuación (más ligero que antes)
        overlay = pg.Surface((sw, sh), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        surface.blit(overlay, (0, 0))

        # Actualizar animación
        if self._anim_progress < 1.0:
            self._anim_progress = min(1.0, self._anim_progress + self._anim_speed)

        # Posición final del diálogo (centrado)
        target_x = (sw - self.dialog_w) // 2
        target_y = (sh - self.dialog_h) // 2

        # Slide desde abajo
        start_y = sh + 20
        t = self._anim_progress
        # uso easing (suave)
        ease = 1 - (1 - t) * (1 - t)
        cur_y = int(start_y + (target_y - start_y) * ease)

        # Diálogo como superficie con alpha
        dialog = pg.Surface((self.dialog_w, self.dialog_h), pg.SRCALPHA)
        # Fondo del cuadro
        bg_color = (245, 245, 245, 255)
        pg.draw.rect(dialog, bg_color, (0, 0, self.dialog_w, self.dialog_h), border_radius=self.border_radius)
        # Borde
        border_color = (50, 50, 60)
        pg.draw.rect(dialog, border_color, (0, 0, self.dialog_w, self.dialog_h), width=3, border_radius=self.border_radius)

        # Marco decorativo adicional (líneas/acento estilo juego)
        self._draw_decorative_frame(dialog)

        # Dibujar la imagen centrada dentro del diálogo dejando padding y espacio para el texto inferior
        if self.image:
            img_rect = self.image.get_rect()
            img_x = (self.dialog_w - img_rect.width) // 2
            img_y = self.padding
            dialog.blit(self.image, (img_x, img_y))

        # Dibujar iconos decorativos en las esquinas del diálogo
        if self._icons:
            # tamaño pequeño para esquinas
            icon_margin = 8
            # top-left
            dialog.blit(self._icons[0], (icon_margin, icon_margin))
            # top-right
            ir = self._icons[1].get_rect()
            dialog.blit(self._icons[1], (self.dialog_w - ir.width - icon_margin, icon_margin))
            # bottom-left
            ib = self._icons[2].get_rect()
            dialog.blit(self._icons[2], (icon_margin, self.dialog_h - ib.height - icon_margin))
            # bottom-right
            ir2 = self._icons[3].get_rect()
            dialog.blit(self._icons[3], (self.dialog_w - ir2.width - icon_margin, self.dialog_h - ir2.height - icon_margin))

        # Texto de instrucción dentro del diálogo
        text = "Presiona X para continuar"
        text_surf = self._font.render(text, True, (30, 30, 30))
        text_rect = text_surf.get_rect()
        text_x = (self.dialog_w - text_rect.width) // 2
        text_y = self.dialog_h - self.padding - text_rect.height
        dialog.blit(text_surf, (text_x, text_y))

        # Aplicar fade según animación
        alpha = int(255 * self._anim_progress)
        if alpha < 255:
            dialog.set_alpha(alpha)

        # Blit al surface principal
        surface.blit(dialog, (target_x, cur_y))

        # Nota: cuando la animación haya terminado, la caja permanece hasta hide() sea llamada.
