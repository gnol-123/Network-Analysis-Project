# Network Analysis Project

YouTube comment analysis for the 2026 Met Gala.

## Setup

Conda is recommended. Use Python 3.10 or newer.

```bash
conda create -n network-analysis python=3.11
conda activate network-analysis
pip install -r requirements.txt
jupyter lab
```

To run the collection notebook, add a `.env` file in the project root:

```bash
YOUTUBE_API_KEY=your_api_key_here
```

Run each notebook with `Kernel > Restart Kernel and Run All Cells`. The only conditional step is the cached RoBERTa model download.

## Run Order

| Notebook | When to run | What it contains |
| --- | --- | --- |
| `01_data_collection.ipynb` | First. Requires `YOUTUBE_API_KEY`. | Uses the YouTube Data API to collect video IDs and comments. Saves `data/video_ids.json` and `data/video_data.json`. |
| `02_data_preprocessing.ipynb` | After `01`. | Flattens comments, removes duplicates, detects language, cleans text, and matches celebrities and brands. Saves `data/video_data_processed.json`. |
| `03_sentiment_analysis.ipynb` | After `02`. | Runs NLTK VADER and Hugging Face RoBERTa sentiment analysis with `cardiffnlp/twitter-roberta-base-sentiment-latest`. Saves `data/video_data_sentiment_processed.json`. |
| `04_network_analysis.ipynb` | After `02`. | Builds NetworkX celebrity and celebrity-brand co-mention graphs. Uses centrality measures, Louvain or greedy modularity communities, and LDA for community topics. Saves graph outputs in `graph_artifacts/`. |
| `05_topic_modelling_and_analysis.ipynb` | After `02` and `03`. | Compares LDA with `CountVectorizer` and NMF with `TfidfVectorizer`, checks Gensim coherence scores, assigns final NMF topics, and reviews topic sentiment and word clouds. |

## Sentiment Analysis Categories

| Category | Contains | Creates |
| --- | --- | --- |
| Entity counts | Celebrity and brand mention counts used for sentiment summaries. | Mention summaries, thresholds, and entity count plots. |
| VADER | NLTK VADER labels for cleaned comment text. | `vader_compound`, `vader_sentiment`, distribution plots, time plots, and entity sentiment plots. |
| RoBERTa | Hugging Face `cardiffnlp/twitter-roberta-base-sentiment-latest` labels and confidence scores. | `bert_sentiment`, class scores, confidence values, distribution plots, entity sentiment plots, and `data/video_data_sentiment_processed.json`. |
| Model comparison | VADER and RoBERTa label agreement checks. | Matching and non-matching sentiment examples. |
