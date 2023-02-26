# Offloading

[![PyPI - Version](https://img.shields.io/pypi/v/offloading.svg)](https://pypi.org/project/offloading)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/offloading.svg)](https://pypi.org/project/offloading)

Offloading tasks in threads or processes

-----

**Table of Contents**

- [Installation](#installation)
- [License](#license)
- [Usage](#usage)

## Installation

```console
pip install offloading
```

## License

`offloading` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

## Usage

```python
from offloading.thread import run_async
from offloading.process import offload, run_async as run_async_proc


def get_result(x):
    print("this is going to be executed in another thread")
    return x * 2


# non-blocking operation
ares = run_async(get_result, 2)  # ares == AsyncResult object
# blocking operation
res = ares.get(timeout=1)  # res == 4


@offload
def heavy_processing(x):
    print("this is going to be executed in separate process")
    return x * 2


# blocking operation
res = heavy_processing(10)  # res == 20


# non-blocking operation
ares = run_async_proc("dotted.path.to.heavy_processing", 5)  # ares = AsyncResult
# blocking operation
res = ares.get(timeout=1)  # res == 10
```

Check out `tests` for more.
