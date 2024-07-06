import subprocess
from libem.match.parameter import batch_size

print("Without batching:")
subprocess.run(['python', '-m', 'benchmark.run', '-p', '10', '--no-shuffle', '--no-log', '-q'])
print()
print(f"With batching (batch size of {batch_size()}):")
subprocess.run(['python', '-m', 'benchmark.run', '-p', '10', '--batch', '--no-shuffle', '--no-log', '-q'])