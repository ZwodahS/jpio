import os
import glob

# http://stackoverflow.com/questions/1057431/loading-all-modules-in-a-folder-in-python
modules = glob.glob(os.path.dirname(__file__)+"/*.py")
__all__ = [ os.path.basename(f)[:-3] for f in modules ]
__all__.remove("__init__")

extensions = __import__("jpio.extensions", fromlist=__all__)

registered_functions = {}

for module in __all__:
    m = getattr(extensions, module)
    if hasattr(m, "functions"):
        for f in m.functions:
            if hasattr(f, "name") and hasattr(f, "allowed_context") and hasattr(f, "args") and hasattr(f, "run"):
                registered_functions[f.name] = f
