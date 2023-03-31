from PySide6.QtGui import QColor

import toml

from as64ui.constants import Directory


class Colours(object):
    app_primary = QColor(30, 37, 42)
    app_secondary = QColor(39, 44, 49)
    window = QColor(60, 63, 65)
    base = QColor(23, 25, 27)
    base_disabled = QColor(40, 42, 44)
    alternate_base = QColor(53, 55, 57)
    highlight = QColor(75, 110, 175)
    light = QColor(105, 108, 122)
    dark = QColor(12, 12, 12)
    tooltip = QColor(255, 255, 255)
    tooltip_text = QColor(255, 255, 255)
    text = QColor(200, 203, 207)
    link = QColor(88, 157, 246)
    button_text = QColor(200, 203, 207)
    bright_text = QColor(255, 0, 0)
    highlight_text = QColor(0, 0, 0)
    tooltip_text = QColor(255, 255, 255)
    button_active = QColor(53, 55, 57)
    button_disabled = QColor(43, 45, 57)
    
    @staticmethod
    def load_theme_colours(theme):
        try:
            with open('{}\{}'.format(Directory.THEMES, theme)) as file:
                data = toml.load(file)
        except FileNotFoundError:
            return False
        except PermissionError:
            return False

        try:
            Colours.window = QColor(*data['base']['window'])
            Colours.text = QColor(*data['text']['window'])
            Colours.link = QColor(*data['text']['link'])
            Colours.base = QColor(*data['base']['base'])
            Colours.alternate_base = QColor(*data['base']['alternate_base'])
            Colours.tooltip = QColor(*data['base']['tooltip'])
            Colours.tooltip_text = QColor(*data['text']['tooltip'])
            Colours.button_active = QColor(*data['button']['active'])
            Colours.button_disabled = QColor(*data['button']['disabled'])
            Colours.button_text = QColor(*data['text']['button'])
            Colours.bright_text = QColor(*data['text']['bright'])
            Colours.highlight = QColor(*data['base']['highlight'])
            Colours.highlight_text = QColor(*data['text']['highlight'])
            Colours.light = QColor(*data['base']['light'])
            Colours.dark = QColor(*data['base']['dark'])
            Colours.app_primary = QColor(*data['app']['primary'])
            Colours.app_secondary = QColor(*data['app']['secondary'])
        except KeyError:
            return False

        return True
