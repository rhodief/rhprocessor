from typing import Any, List
from rhprocessor.controls import DataStore, ULogger, PipeTransporterControl
from rhprocessor.processor import Processor
from rhprocessor.processor import BlockMode, FluxMode, Execute, Processor, ParallelMode, ParallelFluxMode
import time


def carregar(dada: Any, pipe_control: PipeTransporterControl, data_store: DataStore, logger: ULogger):
    logger.log('Iniciando carregar')
    time.sleep(1)
    logger.log('Guardando valor no datastore')
    time.sleep(1)
    _d = data_store.set_data('teste', [9,8,7,6,5,4])
    time.sleep(1)
    logger.log(f'valor bool: {_d}')
    time.sleep(1)
    return [0, 1, 2, 3, 4]

def selecionar(data: Any, pipe_control: PipeTransporterControl, data_store: DataStore, logger: ULogger):
    _val = data_store.get_data('teste')
    time.sleep(1)
    logger.log(f'Valor do datastore: {_val}')
    time.sleep(1)
    logger.log(f'Tentar colocar valor de outro tipo no datastore')
    time.sleep(1)
    _t = data_store.set_data('teste', 'hahahah')
    time.sleep(1)
    logger.log(f'Valor do datastore após tentativa: {_val}, {_t}')
    time.sleep(1)
    return data[0]


class Soma():
    def __init__(self, num = 10) -> None:
        self._num = num
    def __call__(self, data: List[int], pipe_control: PipeTransporterControl, data_store: DataStore, logger: ULogger):
        logger.log('Cheguei em Soma')
        time.sleep(1)
        logger.log('Vou somar cada elemento do array')
        time.sleep(1)
        return [d + self._num for d in data]

def subtrair(data: List[int], pipe_control: PipeTransporterControl, data_store: DataStore, logger: ULogger, num = 5):
    logger.log('Vou subitrair em bloco')
    time.sleep(1)
    return [d - num for d in data]

class SomaFluxo():
    def __init__(self, num = 10) -> None:
        self._num = num
    def __call__(self, data: int, pipe_control: PipeTransporterControl, data_store: DataStore, logger: ULogger) -> Any:
        logger.log('Soma em Fluxo')
        time.sleep(1)
        return data + self._num

class SubtraiFluxo():
    def __init__(self, num = 3) -> None:
        self._num = num
    def __call__(self, data: int, pipe_control: PipeTransporterControl, data_store: DataStore, logger: ULogger) -> Any:
        logger.log('Subtrai em fluxo')
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

import json

#print(json.dumps(proc.to_dict()))
from rhprocessor.output import terminal_logger

terminal_logger(proc)
print('Retorno', proc.data())
print('Controle', json.dumps(proc._transporter.execution_control.tracks.to_dict()))
print('Logger', json.dumps(proc._transporter._logger.get_all_logs()))
