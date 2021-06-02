# rhProcessor

## Overview
rhProcessor organize code pipelines

## Example
1. First, create a function or a class 
```python
## Function-version
def do_something(dada: Any, pipe_control: PipeTransporterControl, data_store: DataStore, logger: ULogger):
    logger.log('Iniciando carregar')
    time.sleep(1)
    logger.log('Guardando valor no datastore')
    time.sleep(1)
    _d = data_store.set_data('teste', [9,8,7,6,5,4])
    time.sleep(1)
    logger.log(f'valor bool: {_d}')
    time.sleep(1)
    return [0, 1, 2, 3, 4]

```


## TODO
1. Flux and ParallelFlux accept iterable. For now, just list
2. Show which function is in execution in real-time