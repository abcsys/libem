import time
import builtins

original_import = builtins.__import__

# Dictionary to store import times
import_times = {}


# Custom import function to measure import times
def custom_import(name, *args, **kwargs):
    start_time = time.perf_counter()
    module = original_import(name, *args, **kwargs)
    end_time = time.perf_counter()
    import_time = (end_time - start_time)

    # Record the import time
    if name in import_times:
        import_times[name] += import_time
    else:
        import_times[name] = import_time

    return module


# Override the built-in import function
builtins.__import__ = custom_import

# Import the main module (this will recursively import submodules)
import libem

# Restore the original import function
builtins.__import__ = original_import

# Sort import times and get the top 30 slowest imports
sorted_import_times = sorted(import_times.items(),
                             key=lambda x: x[1],
                             reverse=True)[:30]

# Print the top slowest imports
print(f"{'Import Time [s]':>15} {'Module':>30}")
for module_name, import_time in sorted_import_times:
    print(f"{import_time:>15.6f} {module_name:>30}")
