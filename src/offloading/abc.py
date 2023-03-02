import abc
import typing as t


class BaseAsyncResult(abc.ABC):
    __slots__ = ()

    @abc.abstractmethod
    def set_result(self, value: t.Any, is_exception: bool = False) -> None:
        ...

    @property
    @abc.abstractmethod
    def is_ready(self) -> bool:
        ...

    @abc.abstractmethod
    def wait(self, timeout: int = None) -> bool:
        ...

    @abc.abstractmethod
    def get(self, timeout: float = None) -> t.Any:
        ...


class BaseAsyncTask(abc.ABC):
    __slots__ = ()

    @property
    @abc.abstractmethod
    def result(self) -> BaseAsyncResult:
        ...

    @abc.abstractmethod
    def start(self) -> None:
        ...
