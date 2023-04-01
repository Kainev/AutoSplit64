global_style_sheet = """

QSpinBox {
    background-color: palette(Window);
    border-radius: 5px;
    padding-left: 10px;
    padding-right: 0px;
    margin: 0px;
}

QSpinBox::down-button {
    background-color: transparent;
}

QSpinBox::down-arrow {
    image: url(resources/icons/down_arrow_16.png);
    width: 12px;
    height: 12px;
}

QSpinBox::up-button {
    background-color: transparent;
}

QSpinBox::up-arrow {
    image: url(resources/icons/up_arrow_16.png);
    width: 12px;
    height: 12px;
}



QSpinBox#NoArrowSpinBox::down-button {
    background-color: transparent;
    width: 0px;
    height: 0px;
}

QSpinBox#NoArrowSpinBox::down-arrow {
    image: none;
}

QSpinBox#NoArrowSpinBox::up-button {
    background-color: transparent;
    width: 0px;
    height: 0px;
}

QSpinBox#NoArrowSpinBox::up-arrow {
    image: none;
}

QLineEdit {
    border-radius: 5px;
}

QLabel#BaseColourLabel {
    background-color: palette(Base);
    color: palette(ButtonText);
}

QLabel:disabled#BaseColourLabel {
    color: rgb(78, 79, 81);
}

QComboBox#WindowColourCombo {
    background-color: palette(Window)
}

QComboBox {
    border-radius: 5px;
    padding-left: 10px;
    padding-right: 32px;
}

QComboBox QFrame
{
    background: palette(Window);
    border-radius: 0px;
    border-width: 2px;
    border-style: solid;
    border-color: palette(Base);
}

QComboBox QListView
{

    background: palette(Window);
}

QComboBox QListView::item
{
    padding: 5px;
    background: palette(Window);
    border-radius: 5px;
    min-height: 27px;
}

QListView::item::selected
{
    border-style: solid;
    border-width: 3px;
    border-color: palette(Highlight);
}

QComboBox::drop-down
{
    border-bottom-right-radius: 5px;
    border-bottom-left-radius: 5px;
}

QComboBox::down-arrow
{
    image: url(resources/icons/down_arrow_32_16.png);
    width: 32px;
    height: 16px;
}


QCheckBox::indicator:unchecked
{
    image: url(resources/icons/checkbox_unchecked_42_14.png);
}

QCheckBox::indicator:checked
{
    image: url(resources/icons/checkbox_checked_42_14.png)
}


QTabBar::tab {
    background: palette(base);
    min-height: 50px;
    font-size: 16px;
}

QTabBar::tab:selected, QTabBar::tab:hover {
    background: palette(highlight);
}

QTabWidget {
    background: palette(base);
    border: none;
}

QTabWidget::pane { border: none; }

"""