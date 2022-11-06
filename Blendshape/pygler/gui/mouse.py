
def buttons_string(buttons):

    button_names = []
    if buttons & NONE:
        button_names.append('NONE')
    if buttons & LEFT:
        button_names.append('LEFT')
    if buttons & MIDDLE:
        button_names.append('MIDDLE')
    if buttons & RIGHT:
        button_names.append('RIGHT')
    return '|'.join(button_names)

# Symbolic names for the mouse buttons
NONE =   1 << 0
LEFT =   1 << 1
MIDDLE = 1 << 2
RIGHT =  1 << 3
