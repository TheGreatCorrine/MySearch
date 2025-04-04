# MySearch: Lightweight Autocomplete Engine Inspired by Google Search

## Overview

**MySearch** is a lightweight Python-based autocompletion engine inspired by the core ideas behind search input suggestions used by platforms like Google. It supports efficient prefix-based querying, weighted suggestion ranking, and scalable word storage using trie (prefix tree) data structures.

Originally developed as a foundation in understanding search engine mechanics, this project replicates some of the underlying principles of large-scale autocomplete systems — on a smaller scale — and is designed for easy integration and educational exploration.

## Key Features

- 🔍 **Prefix-Based Autocompletion**  
  Implements a trie (prefix tree) structure to enable fast lookup and suggestions for partial user inputs.

- ⚖️ **Weighted Ranking Algorithm**  
  Supports weight-based completions, where more frequently used terms can be prioritized, mimicking how real-world search engines rank results.

- 📚 **Scalable Design**  
  Efficiently handles large datasets with structural variation, built to accommodate entries from over 50 different sources with diverse formats.

- 💡 **Modular and Reusable**  
  Clean class-based design enables this engine to be reused in other applications, from command-line interfaces to web-based search tools.

## Installation

```bash
git clone https://github.com/TheGreatCorrine/MySearch.git
cd MySearch
pip install -r requirements.txt  # if applicable
