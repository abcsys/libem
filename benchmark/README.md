# Benchmark Results

## No Schema

### Libem Settings
| Model    | Tools  | Data Preparation                      |
| :------- | :----- | :----------------------------------   |
| `gpt-4o` | Off    | Field values only separated by spaces |

### Accuracy

| Dataset | Precision | Recall | F1  |
| :--- | :---: | :---: | :---: |
| abt-buy | 84.0 | 99.5 | 91.1 |
| amazon-google | 60.0 | 89.7 | 71.9 |
| beer | 92.3 | 85.7 | 88.9 |
| dblp-acm | 80.4 | 100.0 | 89.1 |
| dblp-scholar | 78.4 | 98.8 | 87.4 |
| fodors-zagats | 95.7 | 100.0 | 97.8 |
| itunes-amazon | 87.5 | 77.8 | 82.4 |
| walmart-amazon | 75.4 | 95.3 | 84.2 |

## With Schema

### Libem Settings
| Model    | Tools  | Data Preparation                      |
| :------- | :----- | :----------------------------------   |
| `gpt-4o` | Off    | Schema inline with entity description |

### Replicate
```
python -m benchmark.run --dataset <dataset-name> --num_pairs -1
```

### Accuracy
| Dataset | Precision | Recall | F1  |
| :--- | :---: | :---: | :---: |
| abt-buy | 89.9 | 99.5 | 94.5 |
| amazon-google | 67.4 | 92.7 | 78.1 |
| beer | 92.3 | 85.7 | 88.9 |
| dblp-acm | 94.7 | 99.6 | 97.1 |
| dblp-scholar | 88.3 | 93.6 | 90.9 |
| fodors-zagats | 100.0 | 100.0 | 100.0 |
| itunes-amazon | 100.0 | 63.0 | 77.3 |
| walmart-amazon | 85.4 | 91.2 | 88.2 |
