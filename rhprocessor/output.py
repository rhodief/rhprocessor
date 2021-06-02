from typing import List
from .controls import ACTION_TYPE, ExecutionControl, Logger
from .processor import Processor
import curses
import datetime

FRAME_WIDTH = 100
APP_NAME = 'RhProcessor'
proc_map = None

class Slot():
    def __init__(self, node_dict: dict, logger: Logger, execution_control: ExecutionControl, ids: List[List[int]], current_id_string: str) -> None:
        self._node = node_dict
        self._logger = logger
        self._execution_control = execution_control
        self._ids = ids
        self._slot = {}
        self._current_id_string = current_id_string
    def __call__(self) -> dict:
        return self._digest()
    def _digest(self):
        self._slot['main_header'] = self._node.get('node_type', '').upper() + ': ' + self._node.get('name', '')
        self._slot['sub_header'] = self._fns_to_string(self._node.get('tracks', {}))
        _strt = datetime.datetime.fromtimestamp(self._node.get('start', ''))
        self._slot['start'] = 'Start: ' + _strt.strftime('%d/%m/%Y, %H:%M:%S') + ' (' + str(datetime.datetime.now() - _strt) + ')'
        if self._node.get('node_type') in ['FluxMode', 'ParallelFluxMode']:
            _total = self._node.get('n_chld', None)
            if _total != None:
                n_fns = len(self._node.get('tracks'))
                if n_fns > 0:
                    _exec = len(self._node.get('tracks').get(n_fns - 1))
                    self._slot['info'] = int(_exec/_total * 100)
        
        if self._node.get('node_type') in ['BlockMode', 'FluxMode']:
            _cids = self._current_id_string
            _id_use = None
            _up = -1 if self._node.get('node_type') == 'BlockMode' else - 2
            for id in self._ids:
                _id = self._execution_control._get_key_string(id[:_up])
                if _id == _cids:
                    _id_use = id
                    break
            if _id_use: 
                logs = self._logger.get_log_obj(_id_use)
                if isinstance(logs, list) and len(logs) > 0:
                    self._slot['info_2'] = logs[-1].txt

        return self._slot
    def _fns_to_string(self, fns: dict):
        _fns = []
        for k, v in fns.items():
            if not isinstance(v, dict):
                continue
            is_node = v.get('node_type')
            if is_node:
                _fns.append(v)
            elif v.get(0) and isinstance(v.get(0), dict) and v.get(0).get('node_type'):
                _fns.append(v[0])
        _ret = []
        for i, f in enumerate(_fns):
            if isinstance(f, dict):
                n = f.get('name', '')
                n = f'{i}. {n}'
                _ret.append(n)
        if len(_ret) > 0: _ret[-1] = f'[{_ret[-1]}]'
        return ' '.join(_ret)
        '''
        return {
            'main_header': '',
            'sub_header': '',
            'status': '',
            'duration': '',
            'flux_progress': '',
            'log': '',
            'log_1': ''
        }
        '''
    
    
    
#_node = tracks.getNode(_id[:2]).to_dict()
#log = logger.get_log_obj(_id)

def display_progress(progress: int):
    if progress == None:
        return ''
    SIZE = 40
    fill = round(SIZE * progress / 100)
    blank = SIZE - fill
    return '[' + ('#' * fill) + (' ' * blank) + ']' + ' ' + str(progress) + '%'



console = curses.initscr()

def line_in_frame(txt = '', mask = ' ', start='|', end='|\n', align = 'left', padding = 0) -> str:
    av_area = FRAME_WIDTH - 2 ## Start and end
    av_area -= padding
    mask_space = av_area - len(txt)
    line = ''
    if align == 'right': line += (mask * mask_space) + txt
    elif align == 'center':
        if mask_space % 2 == 0:
            _ms = (mask * int(mask_space / 2))
            line += _ms + txt + _ms
        else:
            _p = int((mask_space / 2) + .5)
            _ms1 = (mask * _p)
            _ms2 = (mask * (_p - 1))
            line += _ms1 + txt + _ms2
    else: 
        line += txt + (mask * mask_space)
    line += end
    line = (' ' * padding) + line
    return start + line
    


def _draw_header(name: str):
    console.addstr(line_in_frame(mask='-'))
    console.addstr(line_in_frame(f' {name} ', mask='#', align='center'))
    console.addstr(line_in_frame(APP_NAME, align='center'))
    console.addstr(line_in_frame(mask ='-'))
    console.addstr(line_in_frame())
    console.refresh()

is_printing = False
def print_slots(_slots):
    global is_printing
    if is_printing:
        return False
    is_printing = True
    console.clrtobot()
    default_padding = 5
    header_height = 5
    def _build_core(ce, lj = 0):
        main_header = ce.get('main_header', '')
        sub_header = ce.get('sub_header', '')
        start = ce.get('start', '')
        flux_progress = ce.get('info', '')
        log = ce.get('info_2', '')
        log_1 = ce.get('info_3', '')
        console.addstr(header_height + ( 6 * lj), 0, line_in_frame(txt=main_header))
        console.addstr((header_height + 1 + (6 * lj)), 0, line_in_frame(sub_header, padding=default_padding))
        console.addstr((header_height + 2 + (6 * lj)), 0, line_in_frame(start, padding=default_padding))
        console.addstr((header_height + 3 + (6 * lj)), 0, line_in_frame(display_progress(flux_progress) if flux_progress else '', padding=default_padding))
        console.addstr((header_height + 4 + (6 * lj)), 0, line_in_frame(txt='logs |  ' + log, padding=default_padding))
        console.addstr((header_height + 5 + (6 * lj)), 0, line_in_frame(txt='     |  ' + log_1, padding=default_padding))
        
    for i, s in enumerate(_slots):
        _build_core(s(), i)
        console.refresh()
    is_printing = False

def terminal_logger(processor: Processor):
    _draw_header(processor.name)
    def _terminal_logger(execution_control: ExecutionControl, logger: Logger, action_type: ACTION_TYPE):
        ids = [v for k, v in execution_control.current_nodes_id.items()]
        slots = [Slot(v.to_dict(), logger, execution_control, ids, k) for k, v in execution_control.current_node.items()]
        print_slots(slots)
    processor.on_change(_terminal_logger)
    #proc_map = processor.to_dict()
    processor()
    curses.endwin()