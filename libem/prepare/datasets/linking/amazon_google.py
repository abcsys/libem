import csv
import gzip
import os

from libem.prepare import datasets

def load(num_samples=-1):
    linking_path = os.path.join(datasets.LIBEM_SAMPLE_DATA_PATH, "linking")
    path = os.path.join(linking_path, "amazon-google")
    left, right, mapping = [], [], []
    
    with gzip.open(os.path.join(path, "Amazon.csv.gz"), 
                   'rt', encoding='utf-8', errors='replace') as f:
        csv_reader = csv.DictReader(f)
        for i, row in enumerate(csv_reader):
            if num_samples > 0 and i == num_samples:
                break

            left.append(row)
    
    with gzip.open(os.path.join(path, "GoogleProducts.csv.gz"), 
                   'rt', encoding='utf-8', errors='replace') as f:
        csv_reader = csv.DictReader(f)
        for i, row in enumerate(csv_reader):
            if num_samples > 0 and i == num_samples:
                break

            right.append(row)
            
    with gzip.open(os.path.join(path, "Amzon_GoogleProducts_perfectMapping.csv.gz"), 
                   'rt', encoding='utf-8', errors='replace') as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            mapping.append(set(row.values()))
    
    return left, right, mapping
