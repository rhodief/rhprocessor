from .processor import Processor
import curses

FRAME_WIDTH = 100
APP_NAME = 'RhProcessor'
proc_map = None


def format_block_mode(data):
    pass



def _current_execution(_data):
    ids = _data.get('ids', None)
    tracks = _data.get('tracks', None)
    logger = _data.get('logger', None)
    if not isinstance(ids, list) or len(ids) < 1: return False
    _ret = {
        'n_num': 0,
        'n_type': '',
        'n_name': '',
        'fn_num': 0,
        'fn_name': '',
        'log_flux_prog': None,
        'log_txt': '',
        'log_txt_prog': None
    }
    for k, _id in ids[:1]:
        _log = logger.get_log_obj(_id)
        _node = tracks.getNode(_id[:2]).to_dict()
        _node_type =_node['node_type']
        _fns = _node['tracks']
        _ret['n_num'] = _id[1]
        _ret['n_type'] = _node['node_type']
        _ret['n_name'] = _node['name']
        if _node_type == 'BlockMode':
            _ret['fn_num'] = _id[-1]
            _ret['fn_name'] = _fns[_id[-1]].get('name')
        elif _node_type in ['ParallelFluxMode', 'FluxMode']:
            _len = len(_fns[0])
            print('Len', _len)
            ### Ao fazer o check-in em FluxMode ou ParallelFluxMode, o tranporter tem o dado e sabe se ele é iterable...
            ### Se for, o que é esperado, ele guarda o o temanho dele no Node criado. Utilizo isso para fazer o progres.. 

        
        #_fn = tracks.getNode(_id).to_dict()
        #print('Fn', _fn)
        #if _lobj != None: 
        #    _ret['log'] = [l.to_dict() for l in _lobj]
    return _ret   
    
    
    

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
    else: line += txt + (mask * mask_space)
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

def _print_current_execution(_ce):
    default_padding = 5
    header_height = 5
    node_txt = '=> Node n. ' + str(int(_ce.get('n_num')) + 1) + ' - ' + _ce.get('n_type') + ': ' + _ce.get('n_name')
    _fns = _ce.get('fn_name')
    func_txt = ''
    if isinstance(_fns, str): func_txt = '-> Function: n. ' + str(int(_ce.get('fn_num')) + 1) + ' - ' + _fns
    elif isinstance(_fns, list): func_txt = '-> Function: ns. ' + ', '.join([n for n in _fns])
    console.addstr(header_height, 0, line_in_frame(txt=node_txt))
    console.addstr((header_height + 1), 0, line_in_frame(func_txt, padding=default_padding))
    console.addstr((header_height + 2), 0, line_in_frame(display_progress(_ce.get('log_flux_prog')), padding=default_padding))
    console.addstr((header_height + 3), 0, line_in_frame(txt='logs |  ' + _ce.get('log_txt'), padding=default_padding))
    if _ce.get('log_txt_prog', None) != None: console.addstr((header_height + 4), 0, line_in_frame(txt='     |  ' + display_progress(_ce.get('log_txt_prog')), padding=default_padding))
    console.refresh()

def terminal_logger(processor: Processor):
    _draw_header(processor.name)
    def _terminal_logger(_data):
        _ce = _current_execution(_data)
        if _ce == False: return False
        _print_current_execution(_ce)
    processor.on_change(_terminal_logger)
    proc_map = processor.to_dict()
    processor()
    curses.endwin()