from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtGui import QBrush, QPainterPath, QPainter, QColor, QPen
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsItem


class RectangleSelector(QGraphicsRectItem):
    handleTopLeft = 1
    handleTopMiddle = 2
    handleTopRight = 3
    handleMiddleLeft = 4
    handleMiddleRight = 5
    handleBottomLeft = 6
    handleBottomMiddle = 7
    handleBottomRight = 8

    handleSize = +8.0
    handleSpace = -4.0

    handleCursors = {
        handleTopLeft: Qt.SizeFDiagCursor,
        handleTopMiddle: Qt.SizeVerCursor,
        handleTopRight: Qt.SizeBDiagCursor,
        handleMiddleLeft: Qt.SizeHorCursor,
        handleMiddleRight: Qt.SizeHorCursor,
        handleBottomLeft: Qt.SizeBDiagCursor,
        handleBottomMiddle: Qt.SizeVerCursor,
        handleBottomRight: Qt.SizeFDiagCursor,
    }

    def __init__(self, *args):
        """
        Initialize the shape.
        """
        super().__init__(*args)
        self.handles = {}
        self.handleSelected = None
        self.mousePressPos = None
        self.mousePressRect = None
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        self.update_handle_pos()

        self.object_name = "RectangleSelector"

    def handle_at(self, point):
        """
        Returns the resize handle below the given point.
        """
        for k, v, in self.handles.items():
            if v.contains(point):
                return k
        return None

    def emit_update(self):
        self.scene().item_update.emit(self)

    def setPos(self, *__args):
        x, y = __args

        offset = self.handleSize + self.handleSpace

        x -= self.boundingRect().left() + offset
        y -= self.boundingRect().top() + offset

        super().setPos(QPointF(x, y))

    def get_view_space_rect(self):
        offset = self.handleSize + self.handleSpace

        return [self.x() + self.boundingRect().left() + offset,
                self.y() + self.boundingRect().top() + offset,
                self.boundingRect().right() - self.boundingRect().left() - (offset * 2),
                self.boundingRect().bottom() - self.boundingRect().top() - (offset * 2)]

    def hoverMoveEvent(self, move_event):
        """
        Executed when the mouse moves over the shape (NOT PRESSED).
        """
        if self.isSelected():
            handle = self.handle_at(move_event.pos())
            cursor = Qt.ArrowCursor if handle is None else self.handleCursors[handle]
            self.setCursor(cursor)
        super().hoverMoveEvent(move_event)

    def hoverLeaveEvent(self, move_event):
        """
        Executed when the mouse leaves the shape (NOT PRESSED).
        """
        self.setCursor(Qt.ArrowCursor)
        super().hoverLeaveEvent(move_event)

    def mousePressEvent(self, mouse_event):
        """
        Executed when the mouse is pressed on the item.
        """
        self.handleSelected = self.handle_at(mouse_event.pos())
        if self.handleSelected:
            self.mousePressPos = mouse_event.pos()
            self.mousePressRect = self.boundingRect()
        super().mousePressEvent(mouse_event)

    def mouseMoveEvent(self, mouse_event):
        """
        Executed when the mouse is being moved over the item while being pressed.
        """
        if self.handleSelected is not None:
            self.interactive_resize(mouse_event.pos())
        else:
            super().mouseMoveEvent(mouse_event)
            self.emit_update()

    def mouseReleaseEvent(self, mouse_event):
        """
        Executed when the mouse is released from the item.
        """
        super().mouseReleaseEvent(mouse_event)
        self.handleSelected = None
        self.mousePressPos = None
        self.mousePressRect = None
        self.update()

    def boundingRect(self):
        """
        Returns the bounding rect of the shape (including the resize handles).
        """
        o = self.handleSize + self.handleSpace
        return self.rect().adjusted(-o, -o, o, o)

    def update_handle_pos(self):
        """
        Update current resize handles according to the shape size and position.
        """
        s = self.handleSize
        b = self.boundingRect()
        self.handles[self.handleTopLeft] = QRectF(b.left(), b.top(), s, s)
        self.handles[self.handleTopMiddle] = QRectF(b.center().x() - s / 2, b.top(), s, s)
        self.handles[self.handleTopRight] = QRectF(b.right() - s, b.top(), s, s)
        self.handles[self.handleMiddleLeft] = QRectF(b.left(), b.center().y() - s / 2, s, s)
        self.handles[self.handleMiddleRight] = QRectF(b.right() - s, b.center().y() - s / 2, s, s)
        self.handles[self.handleBottomLeft] = QRectF(b.left(), b.bottom() - s, s, s)
        self.handles[self.handleBottomMiddle] = QRectF(b.center().x() - s / 2, b.bottom() - s, s, s)
        self.handles[self.handleBottomRight] = QRectF(b.right() - s, b.bottom() - s, s, s)

    def interactive_resize(self, mouse_pos):
        """
        Perform shape interactive resize.
        """
        offset = self.handleSize + self.handleSpace
        bounding_rect = self.boundingRect()
        rect = self.rect()
        diff = QPointF(0, 0)

        self.prepareGeometryChange()

        if self.handleSelected == self.handleTopLeft:
            from_x = self.mousePressRect.left()
            from_y = self.mousePressRect.top()
            to_x = from_x + mouse_pos.x() - self.mousePressPos.x()
            to_y = from_y + mouse_pos.y() - self.mousePressPos.y()
            diff.setX(to_x - from_x)
            diff.setY(to_y - from_y)
            bounding_rect.setLeft(to_x)
            bounding_rect.setTop(to_y)
            rect.setLeft(bounding_rect.left() + offset)
            rect.setTop(bounding_rect.top() + offset)
            self.setRect(rect)

        elif self.handleSelected == self.handleTopMiddle:
            from_y = self.mousePressRect.top()
            to_y = from_y + mouse_pos.y() - self.mousePressPos.y()
            diff.setY(to_y - from_y)
            bounding_rect.setTop(to_y)
            rect.setTop(bounding_rect.top() + offset)
            self.setRect(rect)

        elif self.handleSelected == self.handleTopRight:
            from_x = self.mousePressRect.right()
            from_y = self.mousePressRect.top()
            to_x = from_x + mouse_pos.x() - self.mousePressPos.x()
            to_y = from_y + mouse_pos.y() - self.mousePressPos.y()
            diff.setX(to_x - from_x)
            diff.setY(to_y - from_y)
            bounding_rect.setRight(to_x)
            bounding_rect.setTop(to_y)
            rect.setRight(bounding_rect.right() - offset)
            rect.setTop(bounding_rect.top() + offset)
            self.setRect(rect)

        elif self.handleSelected == self.handleMiddleLeft:
            from_x = self.mousePressRect.left()
            to_x = from_x + mouse_pos.x() - self.mousePressPos.x()
            diff.setX(to_x - from_x)
            bounding_rect.setLeft(to_x)
            rect.setLeft(bounding_rect.left() + offset)
            self.setRect(rect)

        elif self.handleSelected == self.handleMiddleRight:
            from_x = self.mousePressRect.right()
            to_x = from_x + mouse_pos.x() - self.mousePressPos.x()
            diff.setX(to_x - from_x)
            bounding_rect.setRight(to_x)
            rect.setRight(bounding_rect.right() - offset)
            self.setRect(rect)

        elif self.handleSelected == self.handleBottomLeft:
            from_x = self.mousePressRect.left()
            from_y = self.mousePressRect.bottom()
            to_x = from_x + mouse_pos.x() - self.mousePressPos.x()
            to_y = from_y + mouse_pos.y() - self.mousePressPos.y()
            diff.setX(to_x - from_x)
            diff.setY(to_y - from_y)
            bounding_rect.setLeft(to_x)
            bounding_rect.setBottom(to_y)
            rect.setLeft(bounding_rect.left() + offset)
            rect.setBottom(bounding_rect.bottom() - offset)
            self.setRect(rect)

        elif self.handleSelected == self.handleBottomMiddle:
            from_y = self.mousePressRect.bottom()
            to_y = from_y + mouse_pos.y() - self.mousePressPos.y()
            diff.setY(to_y - from_y)
            bounding_rect.setBottom(to_y)
            rect.setBottom(bounding_rect.bottom() - offset)
            self.setRect(rect)

        elif self.handleSelected == self.handleBottomRight:
            from_x = self.mousePressRect.right()
            from_y = self.mousePressRect.bottom()
            to_x = from_x + mouse_pos.x() - self.mousePressPos.x()
            to_y = from_y + mouse_pos.y() - self.mousePressPos.y()
            diff.setX(to_x - from_x)
            diff.setY(to_y - from_y)
            bounding_rect.setRight(to_x)
            bounding_rect.setBottom(to_y)
            rect.setRight(bounding_rect.right() - offset)
            rect.setBottom(bounding_rect.bottom() - offset)
            self.setRect(rect)

        self.emit_update()
        self.update_handle_pos()

    def resize(self, width, height, emit=False):

        offset = self.handleSize + self.handleSpace
        bounding_rect = self.boundingRect()
        rect = self.rect()

        bounding_rect.setRight(bounding_rect.left() + width)
        bounding_rect.setBottom(bounding_rect.top() + height)
        rect.setRight(bounding_rect.right() + offset)
        rect.setBottom(bounding_rect.bottom() + offset)
        self.setRect(rect)
        self.update_handle_pos()

        if emit:
            self.emit_update()

    def shape(self):
        """
        Returns the shape of this item as a QPainterPath in local coordinates.
        """
        path = QPainterPath()
        path.addRect(self.rect())
        if self.isSelected():
            for shape in self.handles.values():
                path.addEllipse(shape)
        return path

    def paint(self, painter, option, widget=None):
        """
        Paint the node in the graphic view.
        """
        painter.setBrush(QBrush(QColor(0, 0, 255, 25)))
        painter.setPen(QPen(QColor(0, 0, 0), 1.0, Qt.SolidLine))
        painter.drawRect(self.rect())

        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(255, 0, 0, 255)))
        painter.setPen(QPen(QColor(0, 0, 0, 255), 1.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        for handle, rect in self.handles.items():
            if self.handleSelected is None or handle == self.handleSelected:
                painter.drawEllipse(rect)


class Rectangle(object):
    def __init__(self, x=0, y=0, width=0, height=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def get(self):
        return [self.x, self.y, self.width, self.height]

    def set(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def get_size(self):
        return [self.width, self.height]

    def set_size(self, width, height):
        self.width = width
        self.height = height

    def get_pos(self):
        return [self.x, self.y]

    def set_pos(self, x, y):
        self.x = x
        self.y = y

    def set_corner_points(self, tl, tr, bl, br=None):
        self.x = tl.x
        self.y = tl.y

        self.width = tr.x - tl.x
        self.height = bl.y - tl.y

    def get_corner_points(self):
        return [Point(self.x, self.y),
                Point(self.x + self.width, self.y),
                Point(self.x + self.width, self.y + self.height),
                Point(self.x, self.y + self.height)]


class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def set(self, x, y):
        self.x = x
        self.y = y

    def get(self):
        return [self.x, self.y]