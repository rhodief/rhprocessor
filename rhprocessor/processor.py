from copy import Error
from types import FunctionType
from typing import Any, List
from multiprocessing import cpu_count
from multiprocessing.dummy import Pool as ThreadPool
from .controls import ACTION_TYPE, DataStore, ExecutionControl, Logger, NodeStatus, PipeData, Transporter
import traceback


class Articulators():
    def __init__(self, *articulators) -> None:
        self._articulators = articulators
        self._name = None
    def set_name(self, name):
        self._name = name
        return self
    @property
    def name(self):
        return self._name if self._name else type(self).__name__
    @property
    def type(self):
        return type(self).__name__
    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'type': self.type,
            'articulators': {k: v.to_dict() for k, v in enumerate(self._articulators)}
        }
        

class Execute():
    def __init__(self, function: FunctionType, params: dict = {}) -> None:
        assert callable(function), f'Param "{function}" is not callable'
        assert isinstance(params, dict), f'Param "{params}" is not dict'
        self._function = function
        self._params = params
        self._type = 'Function Executor'
        self._name = function.__name__ if isinstance(function, FunctionType) else type(function).__name__
    def set_name(self, name):
        self._name = name
        return self
    @property
    def name(self):
        return self._name
    @property
    def type(self):
        return self._type
    def to_dict(self):
        _prm = self._function if isinstance(self._function, FunctionType) else self._function.__init__
        return {
            'name': self.name,
            'type': self.type,
            'parmas': _prm.__code__.co_varnames
        }

    def __call__(self, transporter: Transporter) -> Transporter:
        if transporter.is_on_error():
            transporter.end(status=NodeStatus.ERROR)
            return transporter
        transporter.check_in(self)
        transporter.start()
        try:
            transporter.receive_data(self._function(*transporter.deliver(), **self._params))
            transporter.end()
        except BaseException as e:
            print('############### Function Error ###############')
            print(f'## Function "{self._function.__name__}", node "{transporter._id}": {e}')
            print('@@ Traceback below: ')
            traceback.print_exc()
            transporter.function_error(f'Error on Node {transporter._id}')
            transporter.end(status = NodeStatus.ERROR)
        ## Finaliza transporter
        return transporter

class BlockMode(Articulators):
    def __call__(self, transporter: Transporter) -> Transporter:
        transporter.check_in(self, len(self._articulators))
        for art in self._articulators:
            try:
                transporter = art(transporter)
            except BaseException as e:
                print('Error... ', e)
                traceback.print_exc()
        transporter.check_out(status=NodeStatus.ERROR if transporter.is_on_error() else NodeStatus.SUCCESS)
        return transporter

class FluxMode(Articulators):
    def __call__(self, transporter: Transporter) -> Transporter:
        transporter.check_in(self, len(self._articulators))
        chld_trans = transporter.make_children()
        transporter.set_total_tracks()
        for chld in chld_trans:
            for art in self._articulators:
                try:
                    chld = art(chld)
                except BaseException as e:
                    print('Error , ', e)
        transporter.recompose(chld_trans)
        transporter.check_out(status=NodeStatus.ERROR if transporter.is_on_error() else NodeStatus.SUCCESS)
        return transporter

class ParallelFluxMode(Articulators):
    def _cpus(self, one_free=True):
        one_free = int(one_free)
        return cpu_count() if cpu_count() < 3 else cpu_count() - one_free

    def _map_thread(self, fn, nlist, n_threads = None):
        if (not n_threads) or (n_threads<2):
            n_threads = self._cpus()
        pool = ThreadPool(n_threads)
        pool.map(fn, nlist)
        pool.close()
        pool.join()
    
    def __call__(self, transporter: Transporter) -> Transporter:
        transporter.check_in(self, len(self._articulators))
        chld_trans = transporter.make_children()
        transporter.set_total_tracks()
        def iter_thread(i):
            try:
                for art in self._articulators:
                    chld_trans[i] = art(chld_trans[i])
            except BaseException as e:
                #self._propagarErro(e)
                print('Ops Eerro Thread', e)
        try:
            self._map_thread(fn=iter_thread, nlist=range(len(chld_trans)))
        except BaseException as e:
            print('Error , ', e)
            #traceback.print_exc()
        transporter.recompose(chld_trans)
        transporter.check_out(status=NodeStatus.ERROR if transporter.is_on_error() else NodeStatus.SUCCESS)
        return transporter

class ParallelMode(Articulators):
    def _cpus(self, one_free=True):
        one_free = int(one_free)
        return cpu_count() if cpu_count() < 3 else cpu_count() - one_free

    def _map_thread(self, fn, nlist, n_threads = None):
        if (not n_threads) or (n_threads<2):
            n_threads = self._cpus()
        pool = ThreadPool(n_threads)
        pool.map(fn, nlist)
        pool.close()
        pool.join()
    
    def __call__(self, transporter: Transporter) -> Transporter:
        if transporter.is_on_error():
            transporter.check_out(status=NodeStatus.ERROR)
            return transporter
        len_articulator = len(self._articulators)
        transporter.check_in(self, len_articulator)
        branches = transporter.makeCopy(len_articulator)
        def iter_thread(i):
            #print('\n Iniciando thread', i, '\n')
            try:
                branches[i] = self._articulators[i](branches[i])
            except BaseException as e:
                #self._propagarErro(e)
                print('Ops Eerro Thread', e)
        try:
            self._map_thread(fn=iter_thread, nlist=range(len_articulator))
        except BaseException as e:
            #self._propagarErro(e)
            #raise e
            print('Ops, execucao antes thread', e)
            return
        transporter.recompose(branches)
        transporter.check_out(status=NodeStatus.ERROR if transporter.is_on_error() else NodeStatus.SUCCESS)
        return transporter


class Processor(Articulators):
    def __init__(self, *articulators: List[Articulators]) -> None:
        super().__init__(*articulators)
        self._transporter = Transporter(PipeData(), DataStore(), Logger(), ExecutionControl())
        self._fn = None
        def onChange(action_type: ACTION_TYPE):
            if  not callable(self._fn):
                return
            '''
            _ret =  {
                'ids': [(k, v) for k, v in self._transporter._execution_control.current_node.items()],
                'tracks': self._transporter.execution_control.tracks,
                'logger': self._transporter.logger,
                'type': action_type.name
            }
            '''
            self._fn(self._transporter.execution_control, self._transporter.logger, action_type)
            '''
            _ids = [v for k, v in self._transporter._execution_control.current_node.items()]
            for _id in _ids:
                _ret = {}
                _lobj = self._transporter.logger.get_log_obj(_id)
                _ret['id'] = _id
                _ret['control'] = self._transporter.execution_control.tracks.getNode(_id).to_dict()
                if _lobj != None: 
                    _ret['log'] = [l.to_dict() for l in _lobj]
                self._fn(_ret)
            '''
        self._transporter.on_move(onChange)

    def __call__(self, transporter: Transporter = None) -> Transporter:
        if transporter: self._transporter = transporter
        _transporter = self._transporter
        _transporter.check_in(self, len(self._articulators))
        for art in self._articulators:
            try:
                _transporter = art(_transporter)
            except BaseException as e:
                print('Ops ', e)
                traceback.print_exc()
        _transporter.check_out(status=NodeStatus.ERROR if _transporter.is_on_error() else NodeStatus.SUCCESS)
        self._transporter = _transporter
        return self._transporter

    def data(self):
        return self._transporter.data().data
    def on_change(self, fn):
        self._fn = fn

   