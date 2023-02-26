import logging
import threading
import typing as t

from .abc import BaseAsyncResult, BaseAsyncTask

logger = logging.getLogger(__name__)


class AsyncResult(BaseAsyncResult):
    __slots__ = ("_thread", "_value", "_is_exception")

    def __init__(self, thread: threading.Thread) -> None:
        self._thread = thread
        self._value: t.Any = None
        self._is_exception: t.Optional[bool] = None

    @property
    def thread(self):
        return self._thread

    @property
    def is_ready(self) -> bool:
        return self._is_exception is not None

    def set_result(self, value: t.Any, is_exception: bool = False) -> None:
        if threading.current_thread().ident != self._thread.ident:
            raise RuntimeError("set_result should not be called directly")
        self._value = value
        self._is_exception = is_exception

    def wait(self, timeout: float = None) -> bool:
        self._thread.join(timeout=timeout)
        return self.is_ready

    def get(self, timeout: float = None) -> t.Any:
        if not self.wait(timeout=timeout):
            raise TimeoutError
        if hasattr(self, "_thread"):
            del self._thread
        if self._is_exception:
            raise self._value
        return self._value


class AsyncTask(BaseAsyncTask):
    __slots__ = ("_thread", "_result")

    def __init__(self, func: t.Callable, *args: t.Any, **kwargs: t.Any) -> None:
        self._thread = threading.Thread(target=self.__run, args=(func, *args), kwargs=kwargs)
        self._result = AsyncResult(self._thread)

    @property
    def thread(self) -> threading.Thread:
        return self._thread

    @property
    def result(self) -> AsyncResult:
        return self._result

    def __run(self, func: t.Callable, *args: t.Any, **kwargs: t.Any) -> None:
        try:
            self._result.set_result(func(*args, **kwargs))
        except BaseException as e:
            self._result.set_result(e, is_exception=True)

    def start(self) -> None:
        self._thread.start()


def run_async(func: t.Callable, *args: t.Any, **kwargs: t.Any) -> AsyncResult:
    task = AsyncTask(func, *args, **kwargs)
    task.start()
    return task.result
