# Benchmark Results

To reproduce the benchmark in `/classic`:
```
python -m benchmark.run --name <benchmark-name> --num_pairs -1
```

----

## Data Preparation

### Setup
| Setup   | Model    | Tools | Data Preparation                       |
| :------ | :------- | :---- | :------------------------------------  |
| S1      | `gpt-4o` | Off   | Field values only separated by spaces  |
| S2      | `gpt-4o` | Off   | Schema inline with entity description  |

### Accuracy
| Dataset       | Precision (S1, S2)        | Recall (S1, S2)        | F1 (S1, S2)        |
| :------------ | :-----------------------: | :--------------------: | :----------------: |
| abt-buy       | 84.0, **89.9**             | 99.5, 99.5     | 91.1, **94.5**     |
| amazon-google | 60.0, **67.4**             | 89.7, **92.7**         | 71.9, **78.1**     |
| beer          | 92.3, 92.3         | 85.7, 85.7     | 88.9, 88.9 |
| dblp-acm      | 80.4, **94.7**             | **100.0**, 99.6    | 89.1, **97.1**     |
| dblp-scholar  | 78.4, **88.3**             | 98.8, **93.6**         | 87.4, **90.9**     |
| fodors-zagats | 95.7, **100.0**            | 100.0, 100.0   | 97.8, **100.0**    |
| itunes-amazon | 87.5, **100.0**            | **77.8**, 63.0             | **82.4**, 77.3         |
| walmart-amazon| 75.4, **85.4**             | 95.3, **91.2**         | 84.2, **88.2**     |

