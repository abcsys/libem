# Benchmark Results

Available benchmarks in the `classic` directory:

- [abt-buy](https://github.com/abcsys/libem-sample-data/tree/main/abt-buy)
- [amazon-google](https://github.com/abcsys/libem-sample-data/tree/main/amazon-google)
- [beer](https://github.com/abcsys/libem-sample-data/tree/main/beer)
- [dblp-acm](https://github.com/abcsys/libem-sample-data/tree/main/dblp-acm)
- [dblp-scholar](https://github.com/abcsys/libem-sample-data/tree/main/dblp-scholar)
- [fodors-zagats](https://github.com/abcsys/libem-sample-data/tree/main/fodors-zagats)
- [itunes-amazon](https://github.com/abcsys/libem-sample-data/tree/main/itunes-amazon)
- [walmart-amazon](https://github.com/abcsys/libem-sample-data/tree/main/walmart-amazon)
- [challenging](https://github.com/abcsys/libem-sample-data/tree/main/challenging)

## Blocking

To run the blocking benchmarks in `/classic`:

```
python -m benchmark.run --name <benchmark-name> --block --no-match --num-pairs -1
```

----

### Setup

Each dataset is first separated into two sets containing the left and right entries
respectively, then the two sets are cross joined with blocking acting as a filter.
Finally, each dataset is tuned to achieve a score of 100% in recall by adjusting the
similarity score cutoff between 1-100.

### Results

| Dataset       | Total Pairs | Similarity Cutoff | Percentage Blocked |    F1    |
| :------------ |:-----------:|:-----------------:|:------------------:|:--------:|
| abt-buy       |   367136    |        29         |        27.2        |   1.2    |
| amazon-google |   460106    |        54         |        96.4        |   3.28   |
| beer          |    6308     |        79         |        98.8        |   30.4   |
| dblp-acm      |   678927    |        79         |        99.9        |   50.3   |
| dblp-scholar  |   823244    |        59         |        99.2        |   7.32   |
| fodors-zagats |    13224    |        83         |        99.8        |   80.0   |
| itunes-amazon |    7488     |        63         |        95.8        |   15.2   |
| walmart-amazon|   716846    |        50         |        96.7        |   1.6    |

## Entity Matching

To run the matching benchmarks in `/classic`:

```
python -m benchmark.run --name <benchmark-name> --num-pairs -1
```

----

### Setup

| Setup   | Model    | Tools | Data Preparation                       |
| :------ | :------- | :---- | :------------------------------------  |
| S1      | `gpt-4o` | Off   | Field values only separated by spaces  |
| S2      | `gpt-4o` | Off   | Schema inline with entity description  |

### Results

| Dataset       | Precision (S1, S2) | Recall (S1, S2) |   F1 (S1, S2)   |
| :------------ |:------------------:|:---------------:|:---------------:|
| abt-buy       |   84.0, **89.9**   |   99.5, 99.5    | 91.1, **94.5**  |
| amazon-google |   60.0, **67.4**   | 89.7, **92.7**  | 71.9, **78.1**  |
| beer          |     92.3, 92.3     |   85.7, 85.7    |   88.9, 88.9    |
| dblp-acm      |   80.4, **94.7**   | **100.0**, 99.6 | 89.1, **97.1**  |
| dblp-scholar  |   78.4, **88.3**   | 98.8, **93.6**  | 87.4, **90.9**  |
| fodors-zagats |  95.7, **100.0**   |  100.0, 100.0   | 97.8, **100.0** |
| itunes-amazon |  89.3, **100.0**   | 92.6, **96.3**  | 90.9, **98.11** |
| walmart-amazon|   75.4, **85.4**   | 95.3, **91.2**  | 84.2, **88.2**  |

### Prompt-level batching

To run the benchmark with batching, use the `--batch-size` flag with the desired batch size. For example, to run
the `abt-buy` benchmark with a batch size of 16, use the following command:

```
python -m benchmark.run --name abt-buy --num-pairs -1 --batch-size 16
```

The queries over multiple candidate pairs are grouped into the same prompt request. Each pair is prefixed with "Q#:"

```
# input
Q1:
<pair>
Q2:
<pair>
...

# expected model response
Q1: <ans>
Q2: <ans>
...
```

### Results

Varying batch sizes when performing EM over `abt-buy` dataset.

| Batch Size | F1    | Latency    | Per Pair Latency | Cost |
|:----------:|:-----:|:----------:|:----------------:|:----:|
|     1      | 94.37 |   14.44    | 2.44             | 1.20 |
|   **4**    | 93.78 |  **3.65**  | 0.41             | 1.06 |
|     16     | 94.06 |   11.60    | 0.15             | 1.01 |
|     64     | 94.86 |   11.98    | 0.12             | 0.99 |
|    128     | 94.54 |   22.32    | 0.11             | 0.99 |
|    256     | 93.43 |   32.93    | 0.10             | 0.99 |
|    512     | 70.87 |   74.44    | 0.08             | 0.95 |
