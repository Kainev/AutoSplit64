from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDropEvent
from PyQt5.QtWidgets import QTableWidget, QAbstractItemView, QTableWidgetItem, QComboBox


class TableWidgetDragRows(QTableWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.setDragEnabled(True)
        # self.setAcceptDrops(True)
        # self.viewport().setAcceptDrops(True)
        # self.setDragDropOverwriteMode(False)
        # self.setDropIndicatorShown(True)

        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        # self.setDragDropMode(QAbstractItemView.InternalMove)

    """def dropEvent(self, event: QDropEvent):
        if not event.isAccepted() and event.source() == self:
            drop_row = self.drop_on(event)

            rows = sorted(set(item.row() for item in self.selectedItems()))
            #rows_to_move = [[QTableWidgetItem(self.item(row_index, column_index)) if self.item(row_index, column_index) else self.removeCellWidget(row_index, column_index) for column_index in range(self.columnCount())]
                            #for row_index in rows]

            rows_to_move = []
            for i in range(len(rows)):
                rows_to_move.append([])
                for column_index in range(self.columnCount()):
                    item = self.item(rows[i], column_index)
                    if item:
                        rows_to_move[i].append(QTableWidgetItem(self.item(rows[i], column_index)))
                    else:
                        rows_to_move[i].append(QComboBox(self.cellWidget(rows[i], column_index)))


            for row_index in reversed(rows):
                self.removeRow(row_index)
                if row_index < drop_row:
                    drop_row -= 1

            for row_index, data in enumerate(rows_to_move):
                row_index += drop_row
                self.insertRow(row_index)
                for column_index, column_data in enumerate(data):
                    try:
                        self.setItem(row_index, column_index, column_data)
                    except TypeError:
                        print(column_data)
                        self.setCellWidget(row_index, column_index, column_data)
            event.accept()
            for row_index in range(len(rows_to_move)):
                self.item(drop_row + row_index, 0).setSelected(True)
                self.item(drop_row + row_index, 1).setSelected(True)
        super().dropEvent(event)

    def drop_on(self, event):
        index = self.indexAt(event.pos())
        if not index.isValid():
            return self.rowCount()

        return index.row() + 1 if self.is_below(event.pos(), index) else index.row()

    def is_below(self, pos, index):
        rect = self.visualRect(index)
        margin = 1
        if pos.y() - rect.top() < margin:
            return False
        elif rect.bottom() - pos.y() < margin:
            return True
        # noinspection PyTypeChecker
        return rect.contains(pos, True) and not (int(self.model().flags(index)) & Qt.ItemIsDropEnabled) and pos.y() >= rect.center().y()"""
