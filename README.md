<p align="center">
  <img src="./docs/images/libem.png" alt="libem" style="width: 70%;" />
</p>

**Scalable entity matching with human-level accuracy, powered by LLMs and tooling.**

[Jul'24] [Libem Arena: Online Evaluation and Leaderboard for EM](http://arena.libem.org/)  
[Jun'24] [Liberal Entity Matching as a Compound AI Toolchain](https://arxiv.org/abs/2406.11255)  
[Jun'24] [Presented at Compound AI Systems Workshop - Data + AI Summit 2024](https://github.com/abcsys/public/blob/main/data-ai-summit-24/libem-poster.pdf)

[![Downloads](https://static.pepy.tech/badge/libem)](https://pepy.tech/project/libem) [![Downloads](https://static.pepy.tech/badge/libem/month)](https://pepy.tech/project/libem)

Libem is an open-source, compound AI toolchain designed to perform and streamline entity matching (EM). EM involves identifying whether two descriptions refer to the same entity, a task crucial in data management and integration. Traditional EM methods have evolved from rule-based to LLM-based systems, yet they fall short due to their reliance on static knowledge and rigid, predefined prompts. 

Libem addresses these limitations by adopting a modular, tool-oriented approach. It supports dynamic tool use, self-refinement, and optimization, allowing it to adapt and refine its processes based on the dataset and performance metrics. Unlike existing LLM-based EM systems, which are usually in the form of Python notebooks, Libem offers a composable and reusable toolchain that can be easily incorporated into applications or used as a service via APIs. Specifically, Libem can be used as a library or a CLI tool and can be configured to use different models, tools, and parameters. It supports a variety of models, including GPT-3.5, GPT-4, and Llama3 and includes a set of tools to facilitate entity matching, such as browsing and data preparation. 

---

### Table of Contents
- [Installation](#installation)
- [Libem Usage](#libem-usage)
- [Benchmarks and Arena](#benchmarks-and-arena)
- [Citation & Reading More](#citation--reading-more)

### Installation

To install the Libem library and CLI:

```bash
pip install libem
```

For the latest version, you can install from `main`:

```bash
pip install git+https://github.com/abcsys/libem.git
```

Alternatively, if you are interested in contributing to Libem or running the benchmarks, you can install from source. First clone the repository and run:

```bash
make install
```

After installation, you can run the CLI tool to configure Libem with API key(s):

```bash
libem $ libem configure
Enter OPENAI_API_KEY ('sk-****'):
```
The API key is used to access the OpenAI API. If you don't have an API key, you can get one from the [OpenAI website](https://platform.openai.com/). 

You can now validate the installation:

```bash
libem $ libem match apple orange
Match: no
```

Or run through the EM examples in `/examples`:
```bash
make match
```

### Libem Usage

Libem can be used as a library or as a CLI tool. The library provides a simple API to match two entities:

```python
import libem

e1 = "Dyson Hot+Cool AM09 Jet Focus heater and fan, White/Silver"
e2 = "Dyson AM09 Hot + Cool Jet Focus Fan Heater - W/S"

is_match = libem.match(e1, e2)
```

The CLI tool can be used to match entities from the command line:

```bash
libem $ libem match "Dyson Hot+Cool AM09 Jet Focus heater and fan, White/Silver" "Dyson AM09 Hot + Cool Jet Focus Fan Heater - W/S"
Match: yes
```

Both the library and the CLI tool can be configured to use tools, different LLM models, and other parameters and prompts. For example,

```python
import libem

libem.calibrate({
    "libem.match.parameter.model": "gpt-3.5-turbo",
    "libem.match.parameter.tools": ["libem.browse"],
})
```

This will use the `gpt-3.5-turbo` model and the `libem.browse` tool to match entities.

Libem can be configured to output more information about the matching process, e.g., in the CLI:

```bash 
libem $ libem match apple orange --cot --confidence
Explanation:
 1. **Name Comparison**: The names "apple" and "orange" are different.
2. **Category Comparison**: Both are fruits, but they are distinct types of fruits.
3. **Attributes Comparison**: Apples and oranges have different colors, tastes, and nutritional profiles.
4. **Contextual Usage**: In common language, "apple" and "orange" are used to refer to different fruits.

Match: no
Confidence: 5
```

### Benchmarks and Arena

Libem comes with a benchmarking tool that can be used to easily compare the performance of different configurations of Libem over 10+ common EM datasets such as `amazon-google`, `dblp-acm`, and `abt-buy`. To run these benchmarks, first fetch the datasets in the [libem-sample-data](https://github.com/abcsys/libem-sample-data):

```bash
make data
```

Then, the benchmarking tool can be run invoked as:

```bash
python -m benchmark.run -n amazon-google
```

There are several options available to the benchmarking tool, check out `/benchmark` for more information.

Libem also comes with an online evaluation tool called [Libem Arena](http://arena.libem.org/), where you can _compete_ with Libem, other EM tools, and human annotators to match entities over a variety of datasets. We track the performance of these tools and annotators over time, and provide a leaderboard of the best-performing tools and annotators. 

### Citation & Reading More

If you use Libem in a research paper, please cite our work as follows:

```
@article{fu2024liberal,
  title={Liberal Entity Matching as a Compound AI Toolchain},
  author={Fu, Silvery D and Wang, David and Zhang, Wen and Ge, Kathleen},
  journal={arXiv preprint arXiv:2406.11255},
  year={2024}
}
```

You can also read more about the research behind Libem in the following manuscripts:

* [**Liberal Entity Matching as a Compound AI Toolchain**](https://arxiv.org/abs/2406.11255) (Academic Paper, June 2024) 
* [**Poster: Liberal Entity Matching as a Compound AI Toolchain**](https://github.com/abcsys/public/blob/main/data-ai-summit-24/libem-poster.pdf) (Poster, Compound AI Systems Workshop, San Francisco at Data + AI Summit, June 2024) 
* [**Libem Arena**](http://arena.libem.org/) (Online evaluation, July 2024)

Please report any issues or feedback to the [GitHub repository](libem.org). We welcome contributions and collaborations!
