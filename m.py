from typing import Any, List
from rhprocessor.processor import ParallelMode
from rhprocessor.controls import DataStore, Logger, PipeTransporterControl
from rhprocessor.processor import Processor
from rhprocessor.processor import BlockMode, FluxMode, Execute, Processor
import time

def carregar(dada: Any, pipe_control: PipeTransporterControl, data_store: DataStore, logger: Logger):
    return [0, 1, 2]

def selecionar(data: Any, pipe_control: PipeTransporterControl, data_store: DataStore, logger: Logger):
    return data[0]


class Soma():
    def __init__(self, num = 10) -> None:
        self._num = num
    def __call__(self, data: List[int], pipe_control: PipeTransporterControl, data_store: DataStore, logger: Logger):
        return [d + self._num for d in data]

def subtrair(data: List[int], pipe_control: PipeTransporterControl, data_store: DataStore, logger: Logger, num = 5):
    return [d - num for d in data]

class SomaFluxo():
    def __init__(self, num = 10) -> None:
        self._num = num
    def __call__(self, data: int, pipe_control: PipeTransporterControl, data_store: DataStore, logger: Logger) -> Any:
        return data + self._num

class SubtraiFluxo():
    def __init__(self, num = 3) -> None:
        self._num = num
    def __call__(self, data: int, pipe_control: PipeTransporterControl, data_store: DataStore, logger: Logger) -> Any:
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

### Fazer uma métodos em transporter para settar um erro...
###### Ele vai acessar o node respectivo para colocar o status erro.. 
###### Ele pode propagar-se por todo o pipeline e settar os respectivos status.. 
