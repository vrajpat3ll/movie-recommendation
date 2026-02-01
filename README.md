# Movie-Recommender

This project is aimed at recommending movies or TV shows based on their content (Content-Based Recommendation System).

# Installation

We use `uv` for project and dependency management as well as package management.

> Install `uv` [here](https://docs.astral.sh/uv/getting-started/installation/)!
>
> OR just install using pip, `pip install uv`

Run the follwing commands to start the virtual environment:

```sh
uv sync
```

## Virtual Environment

To activate the environment, run:

```sh
./.venv/Scripts/activate # Windows
source .venv/bin/activate # Linux
```

## Run

To run the project:

```sh
uv run main.py
```

## Download Dataset

```sh
uv run fetch_dataset.py
```
