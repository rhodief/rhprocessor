from multiprocessing.dummy import Process
from typing import Any, List
from rhprocessor.controls import DataStore, ULogger, PipeTransporterControl
from rhprocessor.processor import Processor
from rhprocessor.processor import BlockMode, FluxMode, Execute, Processor, ParallelMode, ParallelFluxMode
import time

def carregar(dada: Any, pipe_control: PipeTransporterControl, data_store: DataStore, logger: ULogger):
    logger.log('Iniciando carregar')
    time.sleep(1)
    logger.log('Guardando valor no datastore')
    _d = data_store.set_data('teste', [9,8,7,6,5,4])
    logger.log(f'valor bool: {_d}')
    return [0, 1, 2, 3, 4]

def selecionar(data: Any, pipe_control: PipeTransporterControl, data_store: DataStore, logger: ULogger):
    _val = data_store.get_data('teste')
    logger.log(f'Valor do datastore: {_val}')
    logger.log(f'Tentar colocar valor de outro tipo no datastore')
    _t = data_store.set_data('teste', 'hahahah')
    logger.log(f'Valor do datastore após tentativa: {_val}, {_t}')
    return data[0]


class Soma():
    def __init__(self, num = 10) -> None:
        self._num = num
    def __call__(self, data: List[int], pipe_control: PipeTransporterControl, data_store: DataStore, logger: ULogger):
        logger.log('Cheguei em Soma')
        time.sleep(1)
        logger.log('Vou somar cada elemento do array')
        return [d + self._num for d in data]

def subtrair(data: List[int], pipe_control: PipeTransporterControl, data_store: DataStore, logger: ULogger, num = 5):
    time.sleep(2)
    return [d - num for d in data]

class SomaFluxo():
    def __init__(self, num = 10) -> None:
        self._num = num
    def __call__(self, data: int, pipe_control: PipeTransporterControl, data_store: DataStore, logger: ULogger) -> Any:
        time.sleep(1)
        return data + self._num

class SubtraiFluxo():
    def __init__(self, num = 3) -> None:
        self._num = num
    def __call__(self, data: int, pipe_control: PipeTransporterControl, data_store: DataStore, logger: ULogger) -> Any:
        time.sleep(1)
        return data - self._num

proc2 = Processor(
    BlockMode(
        Execute(carregar)
    ).set_name('Primeiro Bloco'),
    FluxMode(
        Execute(SomaFluxo(4)),
        Execute(SubtraiFluxo(2))
    ),
    ParallelFluxMode(
        Execute(SomaFluxo(4)),
        Execute(SubtraiFluxo(2))
    ),
    ParallelMode(
        BlockMode(
            Execute(Soma(4)),
            Execute(subtrair, {'num': 2})
        ),
        FluxMode(
            Execute(SomaFluxo(5)),
            Execute(SubtraiFluxo(1))
        )
    ),
).set_name('Projeto Intermediário')

'''
proc = Processor(
    proc2,
    BlockMode(
        Execute(selecionar)
    ),
    FluxMode(
        Execute(SomaFluxo(100)),
        Execute(SubtraiFluxo(2))
    )
).set_name('Projeto Agnes')
'''
import json

#print(json.dumps(proc.to_dict()))
from rhprocessor.output import terminal_logger

terminal_logger(proc2)


'''
import zmq

context = zmq.Context()

#  Socket to talk to server
print("Connecting to hello world server…")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

def change(_log):
    _ret = json.dumps(_log).encode('ascii')
    print(f"Sending request  …")
    socket.send(_ret)

    #  Get the reply.
    message = socket.recv()
    print(f"Received reply  [ {message} ]")

proc.on_change(change)

proc()


print('Retorno', proc.data())
print('Controle', json.dumps(proc._transporter.execution_control.tracks.to_dict()))
print('Logger', json.dumps(proc._transporter._logger.get_all_logs()))
### Fazer uma métodos em transporter para settar um erro...
###### Ele vai acessar o node respectivo para colocar o status erro.. 
###### Ele pode propagar-se por todo o pipeline e settar os respectivos status.. 
socket.send(b'STOP')
socket.close()
'''
import time


'''

'''

'''
import curses
import time

console = curses.initscr()  # initialize is our playground

# this can be more streamlined but it's enough for demonstration purposes...
def draw_board(width, height, charset="+-| "):
    h_line = charset[0] + charset[1] * (width - 2) + charset[0]
    v_line = charset[2] + charset[3] * (width - 2) + charset[2]
    console.clear()
    console.addstr(0, 0, h_line)
    for line in range(1, height):
        console.addstr(line, 0, v_line)
    console.addstr(height-1, 0, h_line)
    console.refresh()

def draw_star(x, y, char="*"):
    console.addstr(x, y, char)
    console.refresh()

draw_board(10, 10)  # draw a board
time.sleep(1)  # wait a second
draw_star(6, 6)  # draw our star
time.sleep(1)  # wait a second
draw_star(6, 6, " ")  # clear the star
draw_star(3, 3)  # place the star on another position
time.sleep(3)  # wait a few seconds

curses.endwin()  # return control back to the console

'''



'''
import curses


def main():

    """
    The curses.wrapper function is an optional function that
    encapsulates a number of lower-level setup and teardown
    functions, and takes a single function to run when
    the initializations have taken place.
    """

    curses.wrapper(curses_main)


def curses_main(w):

    """
    This function is called curses_main to emphasise that it is
    the logical if not actual main function, called by curses.wrapper.
    Its purpose is to call several other functions to demonstrate
    some of the functionality of curses.
    """

    w.addstr("-----------------\n")
    w.addstr("| codedrome.com |\n")
    w.addstr("| curses demo   |\n")
    w.addstr("-----------------\n")
    w.refresh()

    printing(w)

    moving_and_sleeping(w)

    # colouring(w)

    w.addstr("\npress any key to exit...")
    w.refresh()
    w.getch()


def printing(w):

    """
    A few simple demonstrations of printing.
    """

    w.addstr("This was printed using addstr\n\n")
    w.refresh()

    w.addstr("The following letter was printed using addch:- ")
    w.addch('a')
    w.refresh()

    w.addstr("\n\nThese numbers were printed using addstr:-\n{}\n{:.6f}\n".format(123, 456.789))
    w.refresh()


def moving_and_sleeping(w):

    """
    Demonstrates moving the cursor to a specified position before printing,
    and sleeping for a specified period of time.
    These are useful for very basic animations.
    """

    row = 20
    col = 0

    curses.curs_set(False)

    for c in range(65, 91):

        w.addstr(row, col, chr(c))
        w.refresh()
        row += 1
        col += 1
        curses.napms(1000)

    curses.curs_set(True)

    w.addch('\n')


def colouring(w):

    """
    Demonstration of setting background and foreground colours.
    """

    if curses.has_colors():

        curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_RED)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_GREEN)
        curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_CYAN)

        w.addstr("Yellow on red\n\n", curses.color_pair(1))
        w.refresh()

        w.addstr("Green on green + bold\n\n", curses.color_pair(2) | curses.A_BOLD)
        w.refresh()

        w.addstr("Magenta on cyan\n", curses.color_pair(3))
        w.refresh()

    else:

        w.addstr("has_colors() = False\n");
        w.refresh()


main()
'''