from typing import Any, List
from rhprocessor.controls import DataStore, ULogger, PipeTransporterControl
from rhprocessor.processor import Processor
from rhprocessor.processor import BlockMode, FluxMode, Execute, Processor, ParallelMode
import time

def carregar(dada: Any, pipe_control: PipeTransporterControl, data_store: DataStore, logger: ULogger):
    logger.log('Iniciando carregar')
    time.sleep(1)
    logger.log('Vou retornar')
    return [0, 1, 2]

def selecionar(data: Any, pipe_control: PipeTransporterControl, data_store: DataStore, logger: ULogger):
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
        time.sleep(.3)
        return data + self._num

class SubtraiFluxo():
    def __init__(self, num = 3) -> None:
        self._num = num
    def __call__(self, data: int, pipe_control: PipeTransporterControl, data_store: DataStore, logger: ULogger) -> Any:
        time.sleep(.2)
        return data - self._num

proc = Processor(
    BlockMode(
        Execute(carregar)
    ).set_name('Primeiro Bloco'),
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
    BlockMode(
        Execute(selecionar)
    ),
    FluxMode(
        Execute(SomaFluxo(100))
    )
)

proc()

import json
print('Retorno', proc.data())
print('Controle', json.dumps(proc._transporter.execution_control.tracks.to_dict()))
print('Logger', json.dumps(proc._transporter._logger.get_all_logs()))
### Fazer uma métodos em transporter para settar um erro...
###### Ele vai acessar o node respectivo para colocar o status erro.. 
###### Ele pode propagar-se por todo o pipeline e settar os respectivos status.. 

'''
import time
class Teste():
    def __init__(self) -> None:
        self._fn = None
    def on_call(self, fn):
        self._fn = fn

    def __call__(self, ) -> Any:
        time.sleep(1)
        self._fn()
        return [0,1,2]
class Tt():
    def disparar(self):
        print('Disparei')

t = Teste()
tt = Tt()
t.on_call(tt.disparar)
print(t())
'''