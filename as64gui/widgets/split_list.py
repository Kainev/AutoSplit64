from PyQt5 import QtCore, QtGui, QtWidgets


class SplitListWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.splits = []
        self._display_count = 7  # Total number of items to display
        self._display_index = 0  # First item to be displayed
        self._selected_index = 0  # Currently selected item (highlighted)
        self._scroll_steps = 0  # keep track of scroll steps in case users mouse has smaller than usual increments

    def paintEvent(self, event):
        painter = QtGui.QPainter()

        split_height = event.rect().height() / self._display_count
        split_width = event.rect().width()
        text_width = split_width - split_height
        x_pos = split_height
        pixmap_dimension = split_height * 0.8
        pixmap_spacing = (split_height - pixmap_dimension) / 2

        painter.begin(self)

        for i in range(self._display_count):
            try:
                split_index = i + self._display_index
                y_pos = split_height * i

                if split_index == self._selected_index:
                    painter.fillRect(0, y_pos, split_width, split_height, QtWidgets.QApplication.palette().color(QtGui.QPalette.Highlight))

                if self.splits[split_index].pixmap:
                    painter.drawPixmap(pixmap_spacing, split_height * i + pixmap_spacing, pixmap_dimension, pixmap_dimension, self.splits[split_index].pixmap)

                painter.drawText(x_pos, y_pos, text_width, split_height, QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter, self.splits[split_index].text)
            except IndexError:
                pass

        painter.end()

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
            if self._display_index < (len(self.splits) - self._display_count):
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

    def add_split(self, title, icon=None):
        self.splits.append(SplitListItem(title, icon))

    def clear(self):
        self.splits = []
        self._display_index = 0
        self.set_selected_index(0)


class SplitListItem(object):
    def __init__(self, text, pixmap=None):
        self.text = text
        self.pixmap = pixmap
