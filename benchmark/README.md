# Libem Benchmark Results

1. [Available Benchmarks](#available-benchmarks)
2. [Blocking](#blocking)
   - [Setup](#setup)
   - [Results](#results)
3. [Matching](#matching)
   - [GPT-4o](#gpt-4o)
   - [GPT-4o-2024-08-06](#gpt-4o-2024-08-06)
   - [GPT-4o-mini](#gpt-4o-mini)
   - [GPT-4-turbo](#gpt-4-turbo)
   - [GPT-4](#gpt-4)
   - [GPT-3.5-turbo](#gpt-35-turbo)
   - [Meta-Llama3-8B-Instruct-8bit](#meta-llama3-8b-instruct-8bit)
   - [Meta-Llama-3.1-8B-Instruct-8bit (no-schema)](#meta-llama-31-8b-instruct-8bit-no-schema)
4. [Prompt-level Batching](#prompt-level-batching)
   - [Results](#results-1)
5. [Data Preparation](#data-preparation-w-vs-wo-schema)
   - [Setup](#setup-1)
   - [Results](#results-2)

## Available Benchmarks

The `classic` directory includes the following available benchmarks, each using the corresponding dataset:

- [abt-buy](https://github.com/abcsys/libem-sample-data/tree/main/abt-buy): The Abt-Buy dataset derives from the online retailers Abt.com and Buy.com.
- [amazon-google](https://github.com/abcsys/libem-sample-data/tree/main/amazon-google): The Amazon-Google dataset derives from the online retailers Amazon.com and the product search service of Google accessible through the Google Base Data API.
- [beer](https://github.com/abcsys/libem-sample-data/tree/main/beer): This dataset contains beer data from BeerAdvocate and RateBeer. It was created by students in the CS 784 data science class at UW-Madison, Fall 2015, as a part of their class project.
- [dblp-acm](https://github.com/abcsys/libem-sample-data/tree/main/dblp-acm): The DBLP-ACM dataset derives from the DBLP and ACM digital libraries.
- [dblp-scholar](https://github.com/abcsys/libem-sample-data/tree/main/dblp-scholar): The DBLP-Scholar dataset derives from the DBLP and Google Scholar digital libraries.
- [fodors-zagats](https://github.com/abcsys/libem-sample-data/tree/main/fodors-zagats): This dataset contains restaurant data from Fodors and from Zagat.
- [itunes-amazon](https://github.com/abcsys/libem-sample-data/tree/main/itunes-amazon): This dataset contains music data from iTunes and Amazon. It was created by students in the CS 784 data science class at UW-Madison, Fall 2015, as a part of their class project.
- [walmart-amazon](https://github.com/abcsys/libem-sample-data/tree/main/walmart-amazon): The Walmart-Amazon dataset derives from the online retailers Walmart.com and Amazon.com.
- [challenging](https://github.com/abcsys/libem-sample-data/tree/main/challenging): This dataset contains commonly failed benchmark cases from the other 8 datasets.

The `suite` directory contains benchmark suites that deep-dive into aspects of Libem performance.

## Blocking

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

|   Benchmark    | Total Pairs | Similarity Cutoff (0-100) | Percentage Blocked |  F1  | Throughput (pps) |
| :------------: | :---------: | :-----------------------: | :----------------: | :--: | :--------------: |
|    abt-buy*    |   367136    |            50             |        95.6        | 2.54 |      86000       |
| amazon-google  |   460106    |            54             |        96.4        | 2.8  |      79000       |
|      beer      |    6308     |            79             |        98.8        | 30.4 |      59000       |
|    dblp-acm    |   678927    |            79             |        99.9        | 50.3 |      50000       |
|  dblp-scholar  |   823244    |            59             |        99.2        | 7.32 |      56000       |
| fodors-zagats  |    13224    |            83             |        99.8        | 80.0 |      58000       |
| itunes-amazon  |    7488     |            63             |        95.8        | 15.2 |      32000       |
| walmart-amazon |   716846    |            50             |        96.7        | 1.6  |      64000       |

> *abt-buy dataset is blocked without the `description` field.

## Matching

To run a single benchmark in `/classic`:

```
python -m benchmark.run -n <benchmark-name> -p -1
```

To run all the benchmarks with a specific model, choose one of the model suites in `/suite`:

```
python -m benchmark.run -s <suite-name>
```

----

### GPT-4o
> This points to gpt-4o-2024-05-13 as of Aug.14, 2024.

|   Benchmark    | Precision | Recall |  F1   | Cost ($) | Pairs per $ | Throughput (pps) |
| :------------: | :-------: | :----: | :---: | :------: | :---------: | :--------------: |
| abt-buy        |   90.18   | 98.06  | 93.95 |  1.206   |     999     |        95        |
| amazon-google  |   69.71   | 81.97  | 75.35 |  1.045   |    1174     |        75        |
| beer           |   91.67   | 78.57  | 84.62 |  0.06916 |    1315     |        54        |
| dblp-acm       |   96.51   | 99.6   | 98.03 |  1.035   |    1204     |        90        |
| dblp-scholar   |   92.92   | 89.2   | 91.02 |  0.9502  |    1311     |       140        |
| fodors-zagats  |   100     | 95.45  | 97.67 |  0.1674  |    1129     |       120        |
| itunes-amazon  |   100     | 88.46  | 93.88 |  0.1422  |     738     |        46        |
| walmart-amazon |   91.01   | 89.12  | 90.05 |  1.01    |    1181     |       110        |
| **Average**    | **91.50** |**90.05**|**90.57**|**0.7031**| **1131** |    **91.25**     |

### GPT-4o-2024-08-06

| Benchmark      | Precision | Recall |  F1   | Cost ($) | Pairs per $ | Throughput (pps) |
| :-----------:  | :-------: | :----: | :---: | :------: | :---------: | :--------------: |
| abt-buy        |   90.99   | 98.06  | 94.39 | 0.6125   |     1968    |       110        |
| amazon-google  |   67.33   | 87.55  | 76.12 | 0.3845   |     3209    |       110        |
| beer           |   90.91   | 71.4   |  80   | 0.03532  |     2576    |        22        |
| dblp-acm       |   96.15   |  100   | 98.04 | 0.5285   |     2365    |        96        |
| dblp-scholar   |   90.27   | 92.8   | 91.52 | 0.4868   |     2567    |       160        |
| fodors-zagats  |    100    |  100   | 100   | 0.08522  |     2217    |        41        |
| itunes-amazon  |   94.74   | 69.23  |  80   | 0.07175  |     1519    |        29        |
| walmart-amazon |   86.34   | 91.71  | 88.94 | 0.5152   |     2315    |       120        |
| **Average**    | **89.59** |**88.85**|**88.63**|**0.340**| **2342**  |      **86**      |

### GPT-4o-mini

|   Benchmark    | Precision | Recall |  F1   | Cost ($) | Pairs per $ | Throughput (pps) |
| :------------: | :-------: | :----: | :---: | :------: | :---------: | :--------------: |
| abt-buy        |   94.61   |  76.7  | 84.72 |  0.0362  |    33287    |       140        |
| amazon-google  |   68.32   | 76.82  | 72.32 | 0.02291  |    53557    |       110        |
| beer           |    100    | 28.57  | 44.44 | 0.002078 |    43792    |        87        |
| dblp-acm       |   96.79   |  84.4  | 90.17 | 0.03115  |    40032    |       120        |
| dblp-scholar   |   90.75   |  62.8  | 74.23 | 0.02864  |    43505    |       120        |
| fodors-zagats  |    100    | 77.27  | 87.18 | 0.005028 |    37589    |        28        |
| itunes-amazon  |    100    | 46.15  | 63.16 | 0.004256 |    24671    |        34        |
| walmart-amazon |   96.3    | 67.36  | 79.27 | 0.03037  |    39282    |        82        |
| **Average**    | **93.35** |**65.01**|**74.44**|**0.02008**|**39464**|    **90.13**     |

### GPT-4-turbo

|   Benchmark    | Precision | Recall |  F1   | Cost ($) | Pairs per $ | Throughput (pps) |
| :------------: | :-------: | :----: | :---: | :------: | :---------: | :--------------: |
| abt-buy        |   92.06   | 84.47  | 88.1  |  2.486   |     484     |        86        |
| amazon-google  |   69.92   | 73.82  | 71.82 |  1.531   |     801     |       110        |
| beer           |    100    |  50    | 66.67 |  0.1406  |     647     |        63        |
| dblp-acm       |   95.75   | 99.2   | 97.45 |  2.139   |     582     |        79        |
| dblp-scholar   |   95.12   |  78    | 85.71 |  2.064   |     603     |        58        |
| fodors-zagats  |    100    | 86.36  | 92.68 |  0.3252  |     581     |        51        |
| itunes-amazon  |    100    | 57.69  | 73.17 |  0.2998  |     350     |       9.8        |
| walmart-amazon |   92.18   | 85.49  | 88.71 |  2.106   |     566     |        47        |
| **Average**    | **93.13** |**76.88**|**83.04**|**1.3865**|**576**   |    **62.98**     |

### GPT-4

|    Benchmark   | Precision | Recall |  F1   | Cost ($) | Pairs per $ | Throughput (pps) |
| :------------: | :-------: | :----: | :---: | :------: | :---------: | :--------------: |
| abt-buy        |   95.02   |  92.72 | 93.86 |   7.26   |     165     |       140        |
| amazon-google  |   63.44   |  90.13 | 74.47 |   4.44   |     276     |        94        |
| beer           |     90    |  64.29 | 75    |  0.4133  |     220     |        74        |
| dblp-acm       |   96.15   |  100   | 98.04 |   6.232  |     200     |       130        |
| dblp-scholar   |   91.56   |  82.4  | 86.74 |   5.694  |     218     |       130        |
| fodors-zagats  |    100    |  86.36 | 92.68 |  0.9667  |     195     |        73        |
| itunes-amazon  |    100    |  46.15 | 63.16 |   0.853  |     123     |        71        |
| walmart-amazon |   90.91   |  88.08 | 89.47 |   6.032  |     197     |       140        |
| **Average**    | **90.89** |**81.27**|**84.18**|**3.986**| **199**   |    **106.5**     |

### GPT-3.5-turbo

|   Benchmark    | Precision | Recall |  F1   | Cost ($) | Pairs per $ | Throughput (pps) |
| :------------: | :-------: | :----: | :---: | :------: | :---------: | :--------------: |
| abt-buy        |    100    | 15.05  | 26.16 |  0.3649  |    3302     |        22        |
| amazon-google  |   68.6    | 35.62  | 46.89 |  0.2209  |    5554     |       160        |
| beer           |    100    | 35.71  | 52.63 | 0.02057  |    4423     |        78        |
| dblp-acm       |   99.38   |   64   | 77.86 |  0.3106  |    4014     |       140        |
| dblp-scholar   |   92.41   |  29.2  | 44.38 |  0.2834  |    4396     |       150        |
| fodors-zagats  |    100    | 40.91  | 58.06 | 0.04857  |    3891     |        54        |
| itunes-amazon  |    100    | 19.23  | 32.26 | 0.04254  |    2468     |        87        |
| walmart-amazon |   94.44   | 35.23  | 51.32 |  0.3007  |    3967     |       150        |
| **Average**    | **94.35** |**34.37**|**48.70**|**0.1990**|**4001**  |    **105.1**     |

### Meta-Llama3-8B-Instruct-8bit

> Llama model runs on Apple M1 silicon

|   Benchmark    | Precision | Recall |  F1   | Cost ($) | Pairs per $ | Throughput (pps) |
|:--------------:|:---------:|:------:|:-----:|:----------------:|:----------------:|:----------------:|
|    abt-buy     |   70.36   | 95.63  | 81.07 | - | - |       0.74       |
| amazon-google  |   51.46   | 75.54  | 61.22 | - | - |       1.2        |
|      beer      |   90.0    | 64.29  | 75.0  | - | - |       0.89       |
|    dblp-acm    |   88.58   |  90.0  | 89.29 | - | - |       0.99       |
|  dblp-scholar  |   81.68   |  85.6  | 83.59 | - | - |       1.1        |
| fodors-zagats  |   89.47   | 77.27  | 82.93 | - | - |       0.92       |
| itunes-amazon  |   50.0    | 69.23  | 58.06 | - | - |       0.66       |
| walmart-amazon |   54.9    | 87.05  | 67.33 | - | - |       0.98       |
| **Average**    | **72.06**|**80.58**|**74.81**|-|-|   **0.935**    |

### Meta-Llama-3.1-8B-Instruct-8bit (no-schema)

|   Benchmark    | Precision |  Recall   |    F1     | Cost ($) | Pairs per $ | Throughput (pps) |
| :------------: | :-------: | :-------: | :-------: | :------: | :---------: | :--------------: |
|    abt-buy     |   48.79   |   98.06   |   65.16   |    -     |      -      |       1.2        |
| amazon-google  |   37.54   |   93.13   |   53.51   |    -     |      -      |       1.4        |
|      beer      |   66.67   |   100.0   |   80.0    |    -     |      -      |       1.2        |
|    dblp-acm    |   71.84   |   100.0   |   83.61   |    -     |      -      |       1.2        |
|  dblp-scholar  |   70.35   |   96.8    |   81.48   |    -     |      -      |       1.3        |
| fodors-zagats  |   82.61   |   86.36   |   84.44   |    -     |      -      |       1.2        |
| itunes-amazon  |   29.89   |   100.0   |   46.02   |    -     |      -      |       0.87       |
| walmart-amazon |   32.87   |   97.93   |   49.22   |    -     |      -      |       1.1        |
|  **Average**   | **55.07** | **96.54** | **67.93** |  **-**   |    **-**    |     **1.18**     |

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

### Data preparation (w/ vs. w/o schema)

To run a single benchmark in `/classic` without schema:

```
python -m benchmark.run -n <benchmark-name> -p -1 --no-schema
```

#### Setup

| Setup   | Model    | Tools | Data Preparation                       |
| :------ | :------- | :---- | :------------------------------------  |
| S1      | `gpt-4o` | Off   | Field values only separated by spaces  |
| S2      | `gpt-4o` | Off   | Schema inline with entity description  |

#### Results

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
