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

## Entity Blocking

To run a single blocking benchmark in `/classic`:

```
python -m benchmark.run -n <benchmark-name> -p -1 --block --no-match
```

To run all blocking benchmarks:

```
python -m benchmark.run -s block
```

----

### Setup

Each dataset is first separated into two sets containing the left and right entries
respectively, then the two sets are cross joined with blocking acting as a filter.
Finally, each dataset is tuned to achieve a score of 100% in recall by adjusting the
similarity score cutoff between 1-100.

### Results

|   Benchmark   | Total Pairs | Similarity Cutoff (0-100) | Percentage Blocked |    F1    | Throughput (pps) |
| :------------ | :---------: | :-----------------------: | :----------------: | :------: | :--------------: |
| abt-buy*      |   367136    |            50             |        95.6        |   2.54   |      86000       |
| amazon-google |   460106    |            54             |        96.4        |   2.8    |      79000       |
| beer          |    6308     |            79             |        98.8        |   30.4   |      59000       |
| dblp-acm      |   678927    |            79             |        99.9        |   50.3   |      50000       |
| dblp-scholar  |   823244    |            59             |        99.2        |   7.32   |      56000       |
| fodors-zagats |    13224    |            83             |        99.8        |   80.0   |      58000       |
| itunes-amazon |    7488     |            63             |        95.8        |   15.2   |      32000       |
| walmart-amazon|   716846    |            50             |        96.7        |   1.6    |      64000       |

\* abt-buy dataset is blocked without the `description` field.

## Entity Matching

To run a single benchmark in `/classic`:

```
python -m benchmark.run -n <benchmark-name> -p -1
```

To run all the benchmarks with a specific model, choose one of the model suites in `/suite`:

```
python -m benchmark.run -s <suite-name>
```

----

### Setup

| Setup   | Model    | Tools | Data Preparation                       |
| :------ | :------- | :---- | :------------------------------------  |
| S1      | `gpt-4o` | Off   | Field values only separated by spaces  |
| S2      | `gpt-4o` | Off   | Schema inline with entity description  |

### Results

|   Benchmark    | Precision (S1, S2) | Recall (S1, S2)  |   F1 (S1, S2)   |
| :------------- | :----------------: | :--------------: | :-------------: |
| abt-buy        |   84.0, **89.9**   |  99.5, **99.5**  | 91.1, **94.5**  |
| amazon-google  |   60.0, **67.4**   |  89.7, **92.7**  | 71.9, **78.1**  |
| beer           |   92.3, **92.3**   |  85.7, **85.7**  | 88.9, **88.9**  |
| dblp-acm       |   80.4, **94.7**   | **100.0**, 99.6  | 89.1, **97.1**  |
| dblp-scholar   |   78.4, **88.3**   |  98.8, **93.6**  | 87.4, **90.9**  |
| fodors-zagats  |  95.7, **100.0**   | 100.0, **100.0** | 97.8, **100.0** |
| itunes-amazon  |  89.3, **100.0**   |  92.6, **96.3**  | 90.9, **98.11** |
| walmart-amazon |   75.4, **85.4**   |  95.3, **91.2**  | 84.2, **88.2**  |

#### GPT-4o-mini

|   Benchmark    | Precision | Recall |  F1   | Cost ($) | Throughput (pps) |
| :------------- | :-------: | :----: | :---: | :------: | :--------------: |
|    abt-buy     |   94.61   |  76.7  | 84.72 |  0.0362  |       140        |
| amazon-google  |   68.32   | 76.82  | 72.32 | 0.02291  |       110        |
|      beer      |    100    | 28.57  | 44.44 | 0.002078 |        87        |
|    dblp-acm    |   96.79   |  84.4  | 90.17 | 0.03115  |       120        |
|  dblp-scholar  |   90.75   |  62.8  | 74.23 | 0.02864  |       120        |
| fodors-zagats  |    100    | 77.27  | 87.18 | 0.005028 |        28        |
| itunes-amazon  |    100    | 46.15  | 63.16 | 0.004256 |        34        |
| walmart-amazon |   96.3    | 67.36  | 79.27 | 0.03037  |        82        |

#### GPT-4

|    Benchmark   | Precision | Recall |  F1   | Cost ($) | Throughput (pps) |
| :------------- | :-------: | :----: | :---: | :------: | :--------------: |
| abt-buy        |   95.02   |  92.72 | 93.86 |   7.26   |              140 |
| amazon-google  |   63.44   |  90.13 | 74.47 |   4.44   |               94 |
| beer           |     90    |  64.29 | 75    |  0.4133  |               74 |
| dblp-acm       |   96.15   |  100   | 98.04 |   6.232  |              130 |
| dblp-scholar   |   91.56   |  82.4  | 86.74 |   5.694  |              130 |
| fodors-zagats  |    100    |  86.36 | 92.68 |  0.9667  |               73 |
| itunes-amazon  |    100    |  46.15 | 63.16 |   0.853  |               71 |
| walmart-amazon |   90.91   |  88.08 | 89.47 |   6.032  |              140 |

#### GPT-3.5-turbo

|   Benchmark    | Precision | Recall |  F1   | Cost ($) | Throughput (pps) |
| :------------- | :-------: | :----: | :---: | :------: | :--------------: |
|    abt-buy     |    100    | 15.05  | 26.16 |  0.3649  |        22        |
| amazon-google  |   68.6    | 35.62  | 46.89 |  0.2209  |       160        |
|      beer      |    100    | 35.71  | 52.63 | 0.02057  |        78        |
|    dblp-acm    |   99.38   |   64   | 77.86 |  0.3106  |       140        |
|  dblp-scholar  |   92.41   |  29.2  | 44.38 |  0.2834  |       150        |
| fodors-zagats  |    100    | 40.91  | 58.06 | 0.04857  |        54        |
| itunes-amazon  |    100    | 19.23  | 32.26 | 0.04254  |        87        |
| walmart-amazon |   94.44   | 35.23  | 51.32 |  0.3007  |       150        |

### Meta-Llama3-8B-Instruct-8bit

|    Benchmark     | Precision | Recall |  F1   | Cost ($) | Throughput (pps) |
| :------------: | :-------: | :----: | :---: | :------: | :--------------: |
|    abt-buy     |    70.36    | 95.63  | 81.07 |  -  |        0.74        |
| amazon-google  |   51.46    | 75.54  | 61.22 |  -  |       1.2        |
|      beer      |    90.0    | 64.29  | 75.0 | -  |        0.89        |
|    dblp-acm    |   88.58   |   90.0   | 89.29 |  -  |       0.99        |
|  dblp-scholar  |   81.68   |  85.6  | 83.59 |  -  |       1.1        |
| fodors-zagats  |    89.47    | 77.27  | 82.93 | -  |        0.92        |
| itunes-amazon  |    50.0    | 69.23  | 58.06 | -  |        0.66        |
| walmart-amazon |   54.9   | 87.05  | 67.33 |  -  |       0.98        |

For more results on Llama models, please see [Llama.md](Llama.md)

### Prompt-level batching

To run a benchmark with batching, use the `--batch-size` flag with the desired batch size. For example, to run
the `abt-buy` benchmark with a batch size of 16, use the following command:

```
python -m benchmark.run -n abt-buy -p -1 --batch-size 16
```

All candidate pairs in a batch are grouped into the same prompt request. Each pair is prefixed with "Q#:"

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

To run the following batching experiment for a benchmark, use:

```
python -m benchmark.run -s batch -n <benchmark-name>
```

#### Results

Varying the batch size when performing EM over the `abt-buy` benchmark:

| Batch Size | F1    | Latency    | Per Pair Latency | Cost |
|:----------:|:-----:|:----------:|:----------------:|:----:|
|     1      | 94.37 |   14.44    | 2.44             | 1.20 |
|   **4**    | 93.78 |  **3.65**  | 0.41             | 1.06 |
|     16     | 94.06 |   11.60    | 0.15             | 1.01 |
|     64     | 94.86 |   11.98    | 0.12             | 0.99 |
|    128     | 94.54 |   22.32    | 0.11             | 0.99 |
|    256     | 93.43 |   32.93    | 0.10             | 0.99 |
|    512     | 70.87 |   74.44    | 0.08             | 0.95 |
