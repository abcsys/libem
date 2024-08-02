import os
import time


def report_import_time(package_name):
    start = time.time()
    exec(f"import {package_name}")
    return time.time() - start


__dir__ = os.path.dirname(__file__)

if __name__ == "__main__":
    with open(os.path.join(__dir__, "..", "requirements.txt")) as f:
        packages = f.read().splitlines()

    pkg_time = {}

    for pkg in packages:
        if pkg == "pyyaml":
            pkg = "yaml"
        if pkg == "scikit-learn":
            pkg = "sklearn"
        if pkg in {
            "python-Levenshtein",
            "langchain-community",
            "langchain-google-community",
            "google-api-python-client",
            "duckduckgo-search",
        }:
            continue

        elapsed_time = report_import_time(pkg)
        pkg_time[pkg] = elapsed_time

    sorted_pkg_time = sorted(pkg_time.items(), key=lambda x: x[1], reverse=True)
    print(f"{'Import Time [s]':>15} {'Module':>30}")
    for pkg_name, import_time in sorted_pkg_time:
        print(f"{import_time:>15.6f} {pkg_name:>30}")
