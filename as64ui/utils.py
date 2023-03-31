from PySide6.QtWidgets import (
    QMessageBox,
    QErrorMessage
)

from PySide6.QtGui import (
    QPalette,
    QLinearGradient,
    QBrush,
)


def apply_gradient(widget, colour_1, colour_2):
    p = QPalette()
    gradient = QLinearGradient(0, 0, widget.frameGeometry().width(), widget.frameGeometry().height())
    gradient.setColorAt(1.0, colour_1)
    gradient.setColorAt(0.0, colour_2)
    p.setBrush(QPalette.Window, QBrush(gradient))
    widget.setPalette(p)
