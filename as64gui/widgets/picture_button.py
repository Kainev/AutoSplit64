from PyQt5 import QtCore, QtWidgets, QtGui


class PictureButton(QtWidgets.QAbstractButton):
    def __init__(self, pixmap, pixmap_pressed=None, pixmap_hover=None, parent=None):
        super().__init__(parent=parent)
        self.pixmap = pixmap

        if pixmap_pressed:
            self.pixmap_pressed = pixmap_pressed
        else:
            self.pixmap_pressed = pixmap

        self.pixmap_hover = pixmap_hover

        self._text = None
        self._colour = None

    def setText(self, text):
        self._text = text
        self.repaint()
        super().setText(text)

    def setTextColour(self, colour):
        self._colour = colour

    def paintEvent(self, event):
        pix = self.pixmap_hover if self.underMouse() and self.pixmap_hover else self.pixmap
        if self.isDown():
            pix = self.pixmap_pressed

        painter = QtGui.QPainter()
        painter.begin(self)
        painter.drawPixmap(event.rect(), pix)

        if self._text:
            painter.setPen(self.palette().color(QtGui.QPalette.ButtonText))
            painter.drawText(event.rect(), QtCore.Qt.AlignCenter, self._text)
        painter.end()

    def enterEvent(self, event):
        self.update()

    def leaveEvent(self, event):
        self.update()

    def sizeHint(self):
        return self.pixmap.size()


class StateButton(QtWidgets.QAbstractButton):
    def __init__(self, pixmap=None, pixmap_pressed=None, pixmap_hover=None, parent=None):
        super().__init__(parent=parent)
        self.pixmap = pixmap
        self.pixmap_pressed = pixmap_pressed
        self.pixmap_hover = pixmap_hover

        self._text = None
        self._colour = None

        self._states = {}
        self._current_state = None

    def setText(self, text):
        self._text = text
        self.repaint()
        super().setText(text)

    def setTextColour(self, colour):
        self._colour = colour

    def paintEvent(self, event):
        pix = self.pixmap_hover if self.underMouse() and self.pixmap_hover else self.pixmap

        if self.isDown() and self.pixmap_pressed:
            pix = self.pixmap_pressed

        painter = QtGui.QPainter()
        painter.begin(self)
        painter.drawPixmap(event.rect(), pix)

        if self._text:
            painter.setPen(self.palette().color(QtGui.QPalette.ButtonText))
            painter.drawText(event.rect(), QtCore.Qt.AlignCenter, self._text)
        painter.end()

    def enterEvent(self, event):
        self.update()

    def leaveEvent(self, event):
        self.update()

    def sizeHint(self):
        return self.pixmap.size()

    def add_state(self, state, pixmap, text):
        self._states[state] = [pixmap, text]

    def get_state(self):
        return self._current_state

    def set_state(self, state):
        if state in self._states:
            self._current_state = state
            self.pixmap = self._states[state][0]
            self.pixmap_pressed = self._states[state][0]
            self.setText(self._states[state][1])
            self.repaint()
