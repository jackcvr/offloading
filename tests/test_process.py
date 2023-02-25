import pytest

from offloading import process

MP_PARAMS = [
    ([], {}),
    ([1, 2], {}),
    ([3], {"y": 4}),
    ([], {"x": 5, "y": 6}),
]


def get_result(x=None, y=None):
    return dict(x=x, y=y)


@process.offload
def decorated_get_result(*args, **kwargs):
    return get_result(*args, **kwargs)


def get_error(e):
    raise e


@pytest.mark.parametrize(
    "args, kwargs",
    MP_PARAMS,
)
def test_async_task(args, kwargs):
    task = process.AsyncTask(f"{__name__}.get_result", *args, **kwargs)
    assert isinstance(task, process.AsyncTask)
    assert not task.process.is_alive()
    task.start()
    task.result.wait(0.1)
    assert task.result.get(0.1) == get_result(*args, **kwargs)


@pytest.mark.parametrize(
    "args, kwargs",
    MP_PARAMS,
)
def test_run(args, kwargs):
    assert process.run(f"{__name__}.get_result", *args, **kwargs) == get_result(*args, **kwargs)


@pytest.mark.parametrize(
    "args, kwargs",
    MP_PARAMS,
)
def test_run_async(args, kwargs):
    res = process.run_async(f"{__name__}.get_result", *args, **kwargs)
    assert isinstance(res, process.AsyncResult)
    assert res.get() == get_result(*args, **kwargs)


def test_run_async_timeout():
    with pytest.raises(TimeoutError):
        process.run_async("time.sleep", 1).get(0.1)


class SampleError(Exception):
    pass


def test_error():
    with pytest.raises(SampleError):
        process.run(f"{__name__}.get_error", SampleError)


def test_decorator():
    assert decorated_get_result(1, 2) == get_result(1, 2)
