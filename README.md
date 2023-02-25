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
from offloading.process import offload


def get_result():
    print("this is going to be executed in another thread")
    return True


# non-blocking operation
ares = run_async(get_result)  # ares == AsyncResult object
# blocking operation
res = ares.get(timeout=1)  # res == True


@offload
def heavy_processing():
    print("this is going to be executed in separate process")
    return 10


# blocking operation
res = heavy_processing()  # res == 10
```

Check out `tests` for more.
