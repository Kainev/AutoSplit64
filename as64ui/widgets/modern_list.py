from PyQt5.QtCore import(
    Qt,
    QEvent,
    pyqtSignal,
    QRectF
)

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLineEdit,
    QVBoxLayout
)

from PyQt5.QtGui import (
    QPalette,
    QPainter,
    QPainterPath
)


class ModernListWidget(QWidget):
    index_changed = pyqtSignal(int)
    double_clicked = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.menu_items = []
        self._display_count = 7  # Total number of items to display
        self._display_index = 0  # First item to be displayed
        self._selected_index = 0  # Currently selected item (highlighted)
        self._scroll_steps = 0  # keep track of scroll steps in case users mouse has smaller than usual increments
        self._item_height = 0
        
    def paintEvent(self, event):
        painter = QPainter()

        self._item_height = event.rect().height() / self._display_count
        item_width = event.rect().width()
        text_width = item_width - self._item_height
        x_pos = self._item_height * 0.3

        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # painter.fillRect(0, 0, event.rect().width(), event.rect().height(), QApplication.palette().color(QPalette.Base))

        for i in range(self._display_count):
            try:
                index = i + self._display_index
                height = self._item_height
                y_pos = height * i

                height += 1
                
                if index == self._selected_index:
                    # if index == self._display_count - 1:
                    #     height += 1
                    
                    colour = QApplication.palette().color(QPalette.Highlight)
                    # painter.fillRect(0, y_pos, item_width, height,
                    #                  QApplication.palette().color(QPalette.H ighlight))
                elif index % 2 == 0:
                    colour = QApplication.palette().color(QPalette.Base).darker(95)
                    # painter.fillRect(0, y_pos, item_width, height,
                    #                  QApplication.palette().color(QPalette.Base).darker(113))
                else:
                    colour = QApplication.palette().color(QPalette.Base)
                    # painter.fillRect(0, y_pos, item_width, height,
                    #                  QApplication.palette().color(QPalette.Base))
                    
                path = QPainterPath()
                
                if i == 0:
                    path.addRoundedRect(QRectF(0, y_pos, item_width, height / 2), 10, 10)
                    painter.fillPath(path, colour)
                    
                    painter.fillRect(0, y_pos + 10, item_width, height - 10,
                                     colour)
                elif i == self._display_count - 1:
                    path.addRoundedRect(QRectF(0, y_pos + height / 2, item_width, height / 2), 10, 10)
                    painter.fillPath(path, colour)
                    
                    painter.fillRect(0, y_pos, item_width, height - 10,
                                     colour)
                else:
                    painter.fillRect(0, y_pos, item_width, height,
                                     colour)

                painter.drawText(x_pos, y_pos, text_width, self._item_height, Qt.AlignLeft | Qt.AlignVCenter, self.menu_items[index])
            except IndexError:
                pass

        painter.end()
        
    def add_item(self, text):
        self.menu_items.append(text)
        self.repaint()
        
    def set_display_count(self, count):
        self._display_count = count
        
    def wheelEvent(self, event):
        self.scroll_vertically(event.angleDelta())
        event.accept()

    def scroll_vertically(self, steps):
        self._scroll_steps += steps.y()

        if self._scroll_steps >= 120:
            if self._display_index > 0:
                self._display_index -= 1
            self._scroll_steps = 0
        elif self._scroll_steps <= -120:
            if self._display_index < (len(self.menu_items) - self._display_count):
                self._display_index += 1
            self._scroll_steps = 0

        self.repaint()
        
    def set_selected_index(self, index):
        max_displayed_index = self._display_index + self._display_count - 1
        if index > max_displayed_index:
            self._display_index += index - max_displayed_index

        if index < self._display_index:
            self._display_index -= self._display_index - index

        self._selected_index = index
        self.repaint()

        self.index_changed.emit(index)
        
    def eventFilter(self, source, event):
        super().eventFilter(source, event)
        
    def clear(self):
        self.menu_items = []
        self._display_index = 0
        self.set_selected_index(0)