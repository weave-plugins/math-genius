import json
import traceback

try:
    import sympy
except ImportError:
    sympy = None

try:
    import numpy as np
except ImportError:
    np = None

capability = __weave_capability__
params = json.loads(__weave_params__)

real_import = __builtins__["__import__"] if isinstance(__builtins__, dict) else __builtins__.__import__
ALLOWED_MODULES = {
    "math", "cmath", "decimal", "fractions", "random", "statistics",
    "sympy", "numpy", "scipy", "collections", "itertools", "functools", "operator"
}

def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    base_name = name.split(".")[0]
    if base_name in ALLOWED_MODULES:
        return real_import(name, globals, locals, fromlist, level)
    raise ImportError(f"Importing module '{name}' is disallowed in this sandbox.")

# Security model: user-submitted code runs in a restricted namespace.
# Only a curated whitelist of builtins is exposed; dangerous functions such as
# open, eval, exec, and compile are explicitly removed. The code
# still has access to optional math libraries (sympy, numpy) via a safe __import__
# and must assign its answer to a variable named `result`.
SAFE_BUILTINS = {
    "__import__": safe_import,
    "abs": abs,
    "all": all,
    "any": any,
    "bool": bool,
    "complex": complex,
    "dict": dict,
    "divmod": divmod,
    "enumerate": enumerate,
    "Exception": Exception,
    "filter": filter,
    "float": float,
    "format": format,
    "frozenset": frozenset,
    "hasattr": hasattr,
    "hash": hash,
    "hex": hex,
    "int": int,
    "isinstance": isinstance,
    "issubclass": issubclass,
    "iter": iter,
    "len": len,
    "list": list,
    "map": map,
    "max": max,
    "min": min,
    "next": next,
    "oct": oct,
    "ord": ord,
    "pow": pow,
    "range": range,
    "repr": repr,
    "reversed": reversed,
    "round": round,
    "set": set,
    "slice": slice,
    "sorted": sorted,
    "str": str,
    "sum": sum,
    "tuple": tuple,
    "type": type,
    "zip": zip,
}

if capability != "math.solve":
    result = {"error": f"Unknown capability: {capability}"}
else:
    try:
        code = params.get("code", "")
        task = params.get("task", "")

        if not code:
            result = {"error": "No 'code' parameter provided. You must provide python code that sets the 'result' variable."}
        else:
            safe_globals = {"__builtins__": SAFE_BUILTINS}
            if sympy:
                safe_globals["sympy"] = sympy
                safe_globals["sp"] = sympy
            if np:
                safe_globals["numpy"] = np
                safe_globals["np"] = np
            try:
                import math
                safe_globals["math"] = math
            except ImportError:
                pass

            exec(code, safe_globals)

            if "result" not in safe_globals:
                result = {"error": "The execution finished but the 'result' variable was not set."}
            else:
                res = safe_globals["result"]
                result = {
                    "task": task,
                    "success": True,
                    "result_str": str(res),
                    "result_type": type(res).__name__
                }
    except Exception as e:
        result = {"error": str(e), "traceback": traceback.format_exc()}
