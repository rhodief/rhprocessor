from typing import Any, Dict, Iterable, List
from datetime import datetime
import copy

class Logger():
    def log(self, msg):
        pass
    def logProgress(self, progress, total, msg):
        pass

class DataStore():
    def __init__(self, data = {}, protected = True):
        assert isinstance(data, dict), 'Data must be a dict'
        self._data = {}
        self._protected = protected
    def setKey(self, key, data) -> bool:
        if not self._protected or not self._data.get(key) or type(self._data[key]) == type(data):
            self._data[key] = data
            return True
        return False
    def getData(self, key):
        return self._data.get(key)

class PipeInterrupt():
    def __init__(self, msg):
        self._msg = msg
    @property
    def msg(self):
        return self._msg

class PipeStop():
    def __init__(self, msg):
        self._msg = msg
    @property
    def msg(self):
        return self._msg

class PipeError():
    def __init__(self, msg):
        self._msg = msg
    @property
    def msg(self):
        return self._msg

class PipeTransporterControl():
    def error(msg = 'PipeError'):
        return PipeError(msg)

class PipeData():
    def __init__(self, data = None):
        self._data = data
    @property
    def data(self):
        return self._data

class MetaNode():
    def __init__(self, name: str, node_type: str) -> None:
        self._name = name
        self._node_type = node_type
        self._start  = None
        self._end = None
    def to_dict(self):
        return {
            'name': self._name,
            'node_type': self._node_type,
            'start': self._start,
            'end': self._end
        }
class Node(MetaNode):
    def __init__(self, name: str, node_type: str) -> None:
        super().__init__(name, node_type)
        self._tracks: Dict[int, MetaNode] = {}
    @property
    def tracks(self):
        return self._tracks
    def set_tracks_position(self, n_pos, prev = None):
        
        self._tracks = {n: dict() if prev != None else None for n in list(range(n_pos))}
    def add_track(self, key: int, data: MetaNode):
        self._tracks[key] = data
    def to_dict(self):
        _dct = super().to_dict()
        _dct['tracks'] = {}
        for k, v in self._tracks.items():
            if hasattr(v, 'to_dict'):
                _dct['tracks'][k] = v.to_dict()
                continue
            if isinstance(v, dict) and len(v) > 0:
                for _k, _v in v.items():
                    if _dct['tracks'].get(k) == None:
                        _dct['tracks'][k] = {}
                    if hasattr(_v, 'to_dict'):
                        _dct['tracks'][k][_k] = _v.to_dict()
                    if isinstance(_v, dict) and len(_v) > 0:
                        _dct['tracks'][k][_k] = {_kk: _vv.to_dict() if hasattr(_vv, 'to_dict') else _vv for _kk, _vv in _v.items()}
                        continue
                continue
            _dct['tracks'][k] = v
        return _dct
    

class NodeFunctions(MetaNode):
    def __init__(self, name: str, node_type: str) -> None:
        super().__init__(name, node_type)
        self._logs: List[str] = []
    def to_dict(self):
        _dct = super().to_dict()
        _dct['logs'] = self._logs
        return _dct

class Tracks():
    def __init__(self, dict_track = {}) -> None:
        self._tracks = {}
    def addNode(self, nodeKey: List[int], node: MetaNode):
        _list = self._tracks
        for k in nodeKey[:-1]:
            try:
                _list = _list.get(k) if isinstance(_list, dict) else _list.tracks.get(k)
            except BaseException as e:
                raise ValueError(f'Index "{k}" not found in {_list}')
        if isinstance(_list, Node): 
            #print('_list', _list.to_dict())
            _list.add_track(nodeKey[-1], node)
        else: 
            _list[nodeKey[-1]] = node 
    def getNode(self, nodeKey: List[int]):
        list = self._tracks
        for k in nodeKey:
            try:
                _list = _list.get(k)
            except BaseException as e:
                raise ValueError(f'Index "{k}" not found in {_list}')
        return _list
    def to_dict(self):
        return {k: v.to_dict() for k, v in self._tracks.items()}

class ExecutionControl():
    def __init__(self, execution_data: dict = {}):
        self._currentNode: List[int] = [-1] ## stopped. 
        self._tracks = Tracks()
    
    @property
    def currentNode(self):
        return self._currentNode
    @property
    def tracks(self):
        return self._tracks

    '''
    funcao
        nome_execucao
        numero_exeecucao,
        inicio
        fim
        logs []

    Node
        nome_execucao
        numerO-execucao
        inicio
        fim
        Execucoes =>
            Bloco [Funcoes]
            Fluxo [[Funcoes], [Funcoes], [Funcoes]...] Um para cada dado
            Paralelo [Articulador, Articulador...]
    

    
    '''
    pass

class Transporter():
    def __init__(self, pipe_data: PipeData, data_store: DataStore, logger: Logger, execution_control: ExecutionControl, id = [-1], child_id = None):
        self._pipe_data = pipe_data
        self._data_store = data_store
        self._logger = logger
        self._execution_control = execution_control
        self._id = id ## disabled
        self._child_id = child_id ### Quando se tornar filhos, ele tem um ID... 
    @property
    def execution_control(self):
        return self._execution_control
    def check_in(self, articulator, fns_qnt = 0):
        self._id[-1] += 1
        if fns_qnt:
            _inst = Node(articulator.name, articulator.type)
            _prev = None if articulator.type == 'BlockMode' else dict()
            _inst.set_tracks_position(fns_qnt, _prev)
        else:
            ## the children will use this.
            _inst = NodeFunctions(articulator.name, articulator.type)
        _id = self._id if self._child_id == None else self._id + [self._child_id]
        self._execution_control._tracks.addNode(_id, _inst)
        if fns_qnt: self._id.append(-1)
    def make_children(self, qnt = None):
        if not isinstance(self._pipe_data.data, Iterable):
            raise ValueError('Data is not iterable')
        return [self._new_instance(d, i) for i, d in enumerate(self._pipe_data.data)]

    def makeCopy(self, qnt: int):
        n_id = self._id[:]
        del n_id[-1]
        return [self._new_instance(self.data().data, pid=(n_id + [i, -1])) for i in list(range(qnt))]
        
    def _new_instance(self, d, num = None, pid = None):
        _id_list = self._id[:] if not pid else pid
        return Transporter(PipeData(copy.deepcopy(d)), self._data_store, self._logger, self._execution_control, _id_list, num)
    def start(self):
        pass
    
    def end(self):
        pass

    def check_out(self):
        self._id = self._id[:-1]
    
    def deliver(self):
        return self._pipe_data.data, PipeTransporterControl(), self._data_store, self._logger
    def receive_data(self, data: Any):
        if isinstance(data, PipeError) or isinstance(data, PipeInterrupt) or isinstance(data, PipeStop):
            self._pipe_data = data
        else:
            self._pipe_data = PipeData(data)
    def recompose(self, chld_transp: List[Any]):
        self.receive_data([c.data().data if hasattr(c.data(), 'data') else c.data() for c in chld_transp])

    def data(self):
        return self._pipe_data
    


class ProcessorControls():
    pass


