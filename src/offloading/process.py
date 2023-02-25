import multiprocessing as mp
import typing as t
from functools import wraps
from multiprocessing.connection import Connection
from traceback import format_exception
from importlib import import_module

from .abc import BaseAsyncResult, BaseAsyncTask


class RemoteTraceback(Exception):
    def __init__(self, tb) -> None:
        self.tb = tb

    def __str__(self) -> str:
        return self.tb


class ExceptionWithTraceback:
    def __init__(self, exc: BaseException, tb: t.Any) -> None:
        tb = "".join(format_exception(type(exc), exc, tb))
        self.exc = exc
        # Traceback object needs to be garbage-collected as its frames
        # contain references to all the objects in the exception scope
        self.exc.__traceback__ = None
        self.tb = f'\n"""\n{tb}"""'

    def __reduce__(self) -> t.Tuple[t.Callable, t.Tuple[BaseException, t.Any]]:
        return _rebuild_exc, (self.exc, self.tb)


def _rebuild_exc(exc: BaseException, tb: t.Any) -> BaseException:
    exc.__cause__ = RemoteTraceback(tb)
    return exc


class Pipe(t.NamedTuple):
    reader: Connection
    writer: Connection


class AsyncResult(BaseAsyncResult):
    __slots__ = ("_process", "_pipe")

    def __init__(self, process: mp.Process, pipe: Pipe) -> None:
        self._process = process
        self._pipe = pipe

    @property
    def process(self) -> mp.Process:
        return self._process

    def set_result(self, value: t.Any, is_exception: bool = False) -> None:
        self._pipe.writer.send((value, is_exception))
        self._pipe.writer.close()

    @property
    def is_ready(self) -> bool:
        return self._pipe.reader.poll()

    def wait(self, timeout: float = None) -> bool:
        return self._pipe.reader.poll(timeout)

    def get(self, timeout: float = None) -> t.Any:
        if not self.wait(timeout=timeout):
            raise TimeoutError
        try:
            value, is_exception = self._pipe.reader.recv()
            if is_exception:
                raise value
            return value
        finally:
            self._pipe.reader.close()
            self._process.join()
            self._process.close()
            del self._process, self._pipe


class AsyncTask(BaseAsyncTask):
    __slots__ = ("_process", "_result")

    def __init__(self, func: t.Union[str, t.Callable], *args, **kwargs) -> None:
        self._process = mp.Process(target=self.__run, args=(func, *args), kwargs=kwargs)
        self._result = AsyncResult(self._process, Pipe(*mp.Pipe(duplex=False)))

    @property
    def process(self) -> mp.Process:
        return self._process

    @property
    def result(self) -> AsyncResult:
        return self._result

    def __run(self, func: t.Union[str, t.Callable], *args, **kwargs) -> None:
        try:
            if isinstance(func, str):
                module_name, func_name = func.rsplit(".", 1)
                module = import_module(module_name)
                func = getattr(module, func_name)
                if hasattr(func, "__wrapped__"):
                    func = t.cast(t.Callable, func.__wrapped__)
                value = func(*args, **kwargs)
            else:
                value = func(*args, **kwargs)
        except BaseException as e:
            value = ExceptionWithTraceback(e, e.__traceback__)
            self._result.set_result(value, is_exception=True)
        else:
            self._result.set_result(value)

    def start(self) -> None:
        self._process.start()


def run_async(path, *args, **kwargs) -> AsyncResult:
    task = AsyncTask(path, *args, **kwargs)
    task.start()
    return task.result


def run(path, *args, **kwargs) -> t.Any:
    return run_async(path, *args, **kwargs).get()


def offload(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return run(f"{func.__module__}.{func.__name__}", *args, **kwargs)

    wrapper.__wrapped__ = func
    return wrapper
