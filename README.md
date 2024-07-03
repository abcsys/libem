# Libem

An open-source toolchain for fast entity matching with human-level accuracy, powered by LLMs and tools.

## Installation

Run the following command to install Libem library and CLI:

```bash
make install
```

Configure Libem with API keys:

```bash
libem $ libem configure
Enter OPENAI_API_KEY (press Enter to keep the existing key: 'sk-*******************xSAS'):
```
The API key is used to access the OpenAI API. If you don't have an API key, you can get one from the [OpenAI website](https://platform.openai.com/). The key will be stored in the `~/.libem/config.yaml` file.

You can now validate the installation:

```bash
libem $ libem match apple orange
Match: no
```

Or run through the EM examples in `/examples`:
```bash
make examples
```

You can also install the Libem library from `pip`:

```bash
pip install libem
```

## Usage

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

## Benchmarks and Arena

Libem comes with a benchmarking tool that can be used to easily compare the performance of different configurations of Libem over 10+ common EM datasets such as `amazon-google`, `dblp-acm`, and `abt-buy`. To run these benchmarks, first fetch the datasets in the [libem-sample-data](https://github.com/abcsys/libem-sample-data):

```bash
make data
```

Then, the benchmarking tool can be run invoked as:

```bash
python -m benchmark.run -n amazon-google
```

There are several options available to the benchmarking tool, check out `/benchmark` for more information.

## Read More

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

* [**Liberal Entity Matching as a Compound AI Toolchain**](https://arxiv.org/abs/2406.11255) (Academic Paper, Jun 2024) 
* [**Poster: Liberal Entity Matching as a Compound AI Toolchaing**](https://github.com/abcsys/public/blob/main/data-ai-summit-24/libem-poster.pdf) (Poster, Compound AI Systems Workshop, San Francisco at Data + AI Summit, Jun 2024) 
* [**Libem Arena**](http://arena.libem.org/) (Online evaluation tool, Jun 2024)

Please report any issues or feedback to the [GitHub repository](libem.org). We welcome contributions and collaborations!