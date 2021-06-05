# rhProcessor

## Overview
rhProcessor organize code pipelines. All you need is write your functions or classes and connect each other with processor "modes". rhProcessor also exposes a terminal interface to follow up on the entire process throw the nodes. 

## Basic Steps
1. First, create a function or a class according to the example below:
```python
## Function-version
### In this case, a function receive these parameters
def load_data(dada: Any, pipe_control: PipeTransporterControl, data_store: DataStore, logger: ULogger):
    logger.log('Init loading') ## logger object exposes the method "log(msg: str)" in order to register the message in the main processor
    time.sleep(1)
    _d = data_store.set_data('foo', [9,8,7,6,5,4]) ## You can store data in the DataStore setting its key. This instance will be available in all function to retrieve data or store new ones. 
    time.sleep(1)
    logger.log(f'valor bool: {_d}') ## When your store something, by default, it verify the same object type in order to store, otherwise it will return False
    time.sleep(1)
    return [0, 1, 2, 3, 4] ### the function just have to return a value in other to pass it to the next Node. 

## Class-version
### In this case, it's mandatory to implement the method __call__ with the same parameters of the function
### The advantage of this approach is that you can pass parameters in the constructor besides implement a more complex logic inside the class.
class SumValue():
    def __init__(self, num = 10) -> None:
        self._num = num
    def __call__(self, data: List[int], pipe_control: PipeTransporterControl, data_store: DataStore, logger: ULogger):
        time.sleep(1)
        return [d + self._num for d in data]
```
2. Pass the Articulators to the processor object constructor like this:
```python
from rhprocessor.processor import Processor
from rhprocessor.processor import BlockMode, Execute, Processor, ParallelMode, ParallelFluxMode
from rhprocessor.output import terminal_logger

## The functions are called throw the Execute object
processor = Processor(
    BlockMode(
        Execute(load_data),
        Execute(SumValue(10))
    )
).set_name('Project Name') ## You can set the name of the processor

## In this example, load_data will execute and pass the data to SumValue function which it will sum the value 10 for each value of the list, 
## just like implemented in the function. 

terminal_logger(proc) ### this line activate de terminal console. If you just want to execute, you can call processor "processor()"

print('Results', processor.data()) ### Retrieve the value alter all
```
## Articulators
**BlockMode**: it runs one after other, in sequence. 

**FluxMode**: it receive a list of anything, and each item will pass throw the entire process in the block, one at a time

**ParallelFluxMode**: It's the same of "FluxMode", but execute many item at the same time. 

**ParallelMode**: Each child Node will be executed in a new thread. Each of them can be any articulator above, including a processor
