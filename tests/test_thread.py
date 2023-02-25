import time

import pytest

from offloading import thread


class SampleError(Exception):
    pass


def get_result():
    return {"data": "test"}


def raise_error():
    raise SampleError


def test_async_task():
    task = thread.AsyncTask(get_result)
    assert isinstance(task, thread.AsyncTask)
    assert not task.thread.is_alive()
    assert not task.result.is_ready
    task.start()
    task.result.wait(0.05)
    result = task.result.get(timeout=0.1)
    assert result == get_result()


def test_run_async():
    async_res = thread.run_async(get_result)
    assert isinstance(async_res, thread.AsyncResult)
    assert async_res.get(0.1) == get_result()


def test_run_async_error():
    async_res = thread.run_async(raise_error)
    with pytest.raises(SampleError):
        async_res.get(0.1)


def test_run_async_timeout():
    async_res = thread.run_async(time.sleep, 0.2)
    with pytest.raises(TimeoutError):
        async_res.get(timeout=0.1)
