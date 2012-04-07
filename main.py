from __future__ import division

import time

import pyglet
import stackless
import ui
import yaml


key_timeout = 1


def enhanced_user_input():

    root = ui.window_from_dicttree(yaml.load(file('ui.yaml')))
    ui.desktop.add_child(root)

    ch = stackless.channel()
    for id_ in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 
                'delete', 'return', 'star', 'hash']:
        button = ui.desktop.find_window(id_)
        button.callback = lambda btn=button: ch.send(btn.label.text)

    view = ui.desktop.find_window('view')
    text = []
    serial_no = 0

    # In a dict so they can be updated from within inner functions.
    # In Python 3 we'd use `nonlocal` vars.
    current = {'value': None, 'serial': 0}

    def get_current():
        return current['value']

    def set_current(val):
        current['value'] = val

    def wait_and_clear():
        current['serial'] += 1
        serial = current['serial']
        start = time.time()
        while time.time() - start < key_timeout:
            stackless.schedule()
        if current['serial'] == serial:
            current['value'] = None

    while True:
        event = ch.receive()
        if event == 'RET':
            ui.desktop.remove_child(root)
            return ''.join(text)
        elif event == 'DEL':
            set_current(None)
            try:
                del text[-1]
            except IndexError:
                pass
        elif event == get_current():
            index = (index + 1) % len(event)
            text[-1] = event[index]
        else:
            set_current(event)
            index = 0
            text.append(event[0])
        view.set_text(''.join(text))
        stackless.tasklet(wait_and_clear)()

def open_window():
    w = pyglet.window.Window()
    ui.init(w)
    pyglet.clock.schedule(lambda dt: stackless.schedule())
    stackless.tasklet(pyglet.app.run)()
    return w

def close_window():
    pyglet.app.exit()

def run():
    open_window()
    a = enhanced_user_input()
    b = enhanced_user_input()
    close_window()
    print "Got", repr(a), "and", repr(b), "."

def run_repl():
    import code
    def interact():
        w = open_window()
        code.InteractiveConsole(locals=globals()).interact()
        w.close()
    stackless.tasklet(interact)()
    stackless.run()

if __name__ == '__main__':
    stackless.tasklet(run)()
    stackless.run()
