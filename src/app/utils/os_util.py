from PySide6.QtWidgets import QApplication


def ctrl_c(value_to_copy, debug_text: str | None = None):
    """ @debug_text: a string with a single '{copied_value}' placeholder, to be formatted with the value_to_copy """
    clipboard = QApplication.clipboard()
    clipboard.setText(value_to_copy)
    if debug_text:
        print(debug_text.format(copied_value=value_to_copy))
