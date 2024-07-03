# Libem Design
----------------

## Integration

Libem can be used as a CLI tool, over a chat interface (like a chatbot), a web service endpoint, or an embedded library.

Libem enforces a strict naming convention for a toolchain and the tool access methods.
Toolchain's main methods are defined in the interface.py and exposed at the toolchain level.
For example, the following code will import the tune tool in libem toolchain.

```python
from libem import tune
```

To import the libem.tune toolchain, we must explicitly invoke:

```python 
import libem

tune = libem.toolchain("libem.tune") 
```

Note that this does not prevent us from importing the tools in the toolchain directly:

```python
from libem.tune import learn
```

In a nutshell, one can directly import a toolchain's tools but not the tool's module.
This is to _encourage_ (but not enforce) that tools are always accessed via well-defined methods consistent with the LM
access.