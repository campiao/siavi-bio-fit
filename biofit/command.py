command = None

def clear():
    global command
    command = ""

def set_command(value):
    global command
    command = value

def get_command():
    return command