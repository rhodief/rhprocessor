from typing import Any, Dict, Iterable, List
from datetime import datetime
import copy
from enum import Enum, auto


class ACTION_TYPE(Enum):
    CHECKIN_NODE = auto()
    CHECKIN_FN = auto()
    START = auto()
    END = auto()
    CHECKOUT_FN = auto()
    CHECKOUT_NODE = auto()
    LOG = auto()


class ILog():
    def __init__(self, txt) -> None:
        self._txt = txt
        self._dt = datetime.now()
    @property
    def txt(self):
        return self._txt
    @property
    def dt(self):
        return self._dt
    def to_dict(self):
        return {
            'txt': self._txt,
            'dt': datetime.timestamp(self._dt)
        }

class ULogger():
    def __init__(self, obj: List[Dict[str, Any]], _cb_fn = None) -> None:
        self._obj = obj
        self._fn = _cb_fn
    def log(self, msg):
        _o = ILog(msg)
        self._obj.append(_o)
        self._notify(ACTION_TYPE.LOG)

    def logProgress(self, progress, total, msg):
        pass
    def _notify(self, action_type: ACTION_TYPE):
        if callable(self._fn): self._fn(action_type)

class Logger():
    def __init__(self) -> None:
        self._store: Dict[str, List[Dict[str, Any]]] = {}
        self._fn = None
    def get_log_obj_from_string(self, idstring):
        return self._store.get(idstring, None)
    def get_log_obj(self, key: List[int]):
        _id = self._id_string(key)
        return self._store.get(_id, None)
    def _id_string(self, id):
        return '.'.join([str(i) for i in id])
    def u_logger(self, id: List[int]):
        _id = self._id_string(id)
        self._store[_id] = []
        return ULogger(self.get_log_obj_from_string(_id), self._fn)
    def get_all_logs(self):
        return {k: [l.to_dict() for l in v] for k, v in self._store.items()}
    def on_log(self, fn):
        self._fn = fn
    
    
    

class DataStore():
    def __init__(self, data = {}, protected = True):
        assert isinstance(data, dict), 'Data must be a dict'
        self._data = {}
        self._protected = protected
    def set_data(self, key, data) -> bool:
        if not self._protected or not self._data.get(key) or type(self._data[key]) == type(data):
            self._data[key] = data
            return True
        return False
    def get_data(self, key):
        return self._data.get(key)

class MetaError():
    def __init__(self, msg):
        self._msg = msg
    @property
    def msg(self):
        return self._msg

class PipeInterrupt(MetaError):
    pass

class PipeStop(MetaError):
    pass

class PipeError(MetaError):
    pass

class FunctionError(MetaError):
    pass

class PipeTransporterControl():
    def pipe_error(self, msg = 'PipeError'):
        return PipeError(msg)
    def function_error(self, msg):
        return FunctionError(msg = 'User Function Error')

class PipeData():
    def __init__(self, data = None):
        self._data = data
    @property
    def data(self):
        return self._data

class NodeStatus(Enum):
    AWAITING = auto()
    SUCCESS = auto()
    ERROR = auto()
    IGNORED = auto()
    RUNNING = auto()

class MetaNode():
    def __init__(self, name: str, node_type: str) -> None:
        self._name = name
        self._node_type = node_type
        self._start  = None
        self._end = None
        self._status = NodeStatus.AWAITING
        self._n_chld = None
    def set_start(self, value):
        self._start = value
    def set_end(self, value):
        self._end = value
    def set_status(self, status):
        if status not in [ns for ns in NodeStatus]:
            raise ValueError('Status not valid')
        self._status = status
    def set_n_chld(self, n_tracks):
        self._n_chld = n_tracks
    def to_dict(self):
        return {
            'name': self._name,
            'node_type': self._node_type,
            'start': datetime.timestamp(self._start) if isinstance(self._start, datetime) else self._start,
            'end': datetime.timestamp(self._end) if isinstance(self._end, datetime) else self._end,
            'status': self._status.name,
            'n_chld': self._n_chld
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
        _list = self._tracks
        for k in nodeKey:
            try:
                _list = _list.get(k) if isinstance(_list, dict) else _list.tracks.get(k)
            except BaseException as e:
                raise ValueError(f'Index "{k}" not found in {_list}')
        return _list
    def to_dict(self):
        return {k: v.to_dict() for k, v in self._tracks.items()}


class ExecutionControl():
    def __init__(self, execution_data: dict = {}):
        self._current_nodes_id = {}
        self._current_node = {}
        self._tracks = Tracks()
    
    @property
    def current_nodes_id(self):
        return self._current_nodes_id
    @property
    def current_node(self):
        return self._current_node
    @property
    def tracks(self):
        return self._tracks
    def add_execution(self, node_id: List[int]):
        self._current_nodes_id[self._get_key_string(node_id)] = node_id
    def remove_execution(self, node_id: List[int]):
        self._current_nodes_id.pop(self._get_key_string(node_id), None)
    def add_node(self, node_id: List[int], node):
        _kr = None
        for k, _ in self._current_node.items():
            k_list = self._get_key_list(k)
            if (self._is_child(k_list, node_id)):
                _kr = k_list
        if _kr: self.remove_node(k_list)
        self._current_node[self._get_key_string(node_id)] = node
    def remove_node(self, node_id: List[int]):
        self._current_node.pop(self._get_key_string(node_id), None)
    def _is_child(self, parent_id: List[int], child_id: List[int]):
        _test_child = child_id[:-1]
        return parent_id == _test_child
    def _get_key_string(self, node_id: List[int]):
        return '.'.join([str(n) for n in node_id])
    def _get_key_list(self, node_id_string: str):
        return [int(n) for n in node_id_string.split('.')]
class Transporter():
    def __init__(
            self, pipe_data: PipeData, 
            data_store: DataStore, 
            logger: Logger, 
            execution_control: ExecutionControl, 
            id = [-1], child_id = None,
            fn_move = None
        ):
        self._pipe_data = pipe_data
        self._data_store = data_store
        self._logger = logger
        self._execution_control = execution_control
        self._id = id ## disabled
        self._child_id = child_id ### Quando se tornar filhos, ele tem um ID... 
        self._n_children = None
        self._start = None
        self._end = None
        self._error = isinstance(self._pipe_data.data, MetaError)
        self._on_move_fn = fn_move
    @property
    def execution_control(self):
        return self._execution_control
    @property
    def logger(self):
        return self._logger
    def check_in(self, articulator, fns_qnt = 0):
        self._id[-1] += 1
        _id = self._id if self._child_id == None else self._id + [self._child_id]
        if fns_qnt:
            _inst = Node(articulator.name, articulator.type)
            _prev = None if articulator.type == 'BlockMode' else dict()
            _inst.set_tracks_position(fns_qnt, _prev)
            _inst.set_start(datetime.now())
            _inst.set_status(NodeStatus.RUNNING)
            self._execution_control.add_node(_id, _inst)
        else:
            ## the children will use this.
            _inst = NodeFunctions(articulator.name, articulator.type)
        self._execution_control._tracks.addNode(_id, _inst)
        if fns_qnt: self._id.append(-1)
        type_node = ACTION_TYPE.CHECKIN_NODE if isinstance(_inst, Node) else ACTION_TYPE.CHECKIN_FN
        self._notify(type_node)
    def make_children(self, qnt = None):
        if self._error or isinstance(self._pipe_data.data, MetaError):
            return [self._new_instance(d, i) for i, d in enumerate([self._pipe_data.data])]
        if not isinstance(self._pipe_data.data, Iterable):
            raise ValueError('Data is not iterable')
        self._n_children = len(self._pipe_data.data)
        return [self._new_instance(d, i) for i, d in enumerate(self._pipe_data.data)]

    def makeCopy(self, qnt: int):
        n_id = self._id[:]
        del n_id[-1]
        return [self._new_instance(self.data().data, pid=(n_id + [i - 1])) for i in list(range(qnt))]
        
    def _new_instance(self, d, num = None, pid = None):
        _id_list = self._id[:] if not pid else pid
        return Transporter(PipeData(copy.deepcopy(d)), self._data_store, self._logger, self._execution_control, _id_list, num, self._on_move_fn)
    def set_total_tracks(self):
        _id = self._id[:-1]
        node = self._execution_control._tracks.getNode(_id)
        node.set_n_chld(self._n_children)

    def start(self):
        self._start = datetime.now()
        _id = self._id[:]
        if self._child_id != None: _id = _id + [self._child_id]
        node = self._execution_control._tracks.getNode(_id)
        node.set_start(self._start)
        node.set_status(NodeStatus.RUNNING)
        self._execution_control.add_execution(_id)
        self._notify(ACTION_TYPE.START)
        
    
    def end(self, status = NodeStatus.SUCCESS):
        self._end = datetime.now()
        _id = self._id[:]
        if self._child_id != None: _id = _id + [self._child_id]
        node = self._execution_control._tracks.getNode(_id)
        node.set_end(self._end)
        node.set_status(status)
        self._execution_control.remove_execution(_id)
        self._notify(ACTION_TYPE.END)
        
    
    def check_out(self, status = NodeStatus.SUCCESS):
        self._id = self._id[:-1]
        node = self._execution_control._tracks.getNode(self._id)
        node.set_end(datetime.now())
        node.set_status(status)
        self._execution_control.remove_node(self._id)
        type_node = ACTION_TYPE.CHECKOUT_NODE if isinstance(node, Node) else ACTION_TYPE.CHECKOUT_FN
        self._notify(type_node)

    def on_move(self, fn):
        self._on_move_fn = fn
        self._logger.on_log(fn)
    
    def deliver(self):
        _id = self._id[:]
        if self._child_id != None: _id = _id + [self._child_id]
        return self._pipe_data.data, PipeTransporterControl(), self._data_store, self._logger.u_logger(_id)
    def receive_data(self, data: Any):
        if isinstance(data, PipeError) or isinstance(data, PipeInterrupt) or isinstance(data, PipeStop):
            self._pipe_data = data
        else:
            self._pipe_data = PipeData(data)
    def recompose(self, chld_transp: List[Any]):
        self.receive_data([c.data().data if hasattr(c.data(), 'data') else c.data() for c in chld_transp])

    def data(self):
        return self._pipe_data
    def is_on_error(self) -> bool:
        return self._error
    def function_error(self, msg = 'User Error'):
        _err = PipeTransporterControl().function_error(msg)
        self.receive_data(_err)
        self._error = True
    def _notify(self, action_type: ACTION_TYPE):
        if callable(self._on_move_fn): self._on_move_fn(action_type)

