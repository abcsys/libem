# Libem

Libem is an open-source compound AI toolchain for fast and accurate entity matching, powered by LLMs.

## Installation

```bash
make install
``` 

Update `~/.libem/config.yaml` with 
> OPENAI_API_KEY: your key 

Optionally, to support browsing:
> GOOGLE_CSE_ID: your key

And: 
> GOOGLE_API_KEY: your key

To run the sample example.
```bash
make run
```

You can also install libem library with pip:
```bash
pip install libem
```

## Usage

```python
import libem
libem.match("apple", "orange")
```

In shell:
```bash
libem apple orange
```
