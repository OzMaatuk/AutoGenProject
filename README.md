## AutoGen Discussion Engine for NLP Tasks

This repository contains an AutoGen project that facilitates discussions between OpenAI ChatGPT and Google Bard to achieve NLP tasks collaboratively.

**Project Goal:** Automate NLP tasks through controlled conversations between large language models (LLMs).

**Application:** Generate product descriptions, design software architectures, write scripts, etc.

**Key Features:**

* **Multi-model collaboration:** Bard and ChatGPT work together for a broader range of capabilities.
* **Retrieval-augmented generation:** Documents are used to enhance the LLMs' responses.
* **Manager-led discussion:** A separate LLM guides the conversation flow and prompts the main LLMs.
* **Flexible configuration:** Adjust conversation parameters like task, document set, and LLM settings.

**Project Structure:**

* `SettlementChat.py`: Handles core functionalities like conversation initiation, message exchange, and summary generation.
* `main.ipynb`: Demonstrates example usage for product development tasks.
* `logs`: Stores conversation logs for each role (PM, Architect, Programmer).
* `prompts`: Text files containing initial prompts for each role.
* `rag`: Documents used for retrieval-augmented generation.

**Getting Started:**

1. Install AutoGen and its dependencies.
2. Configure the `CONFIG_LIST.json` file with LLM settings and document paths.
3. Run the `main.ipynb` notebook for a guided product development example.
4. Adapt the code to your specific NLP tasks and prompts.

**Benefits:**

* **Improves NLP results:** Combining two powerful LLMs with document retrieval leads to more comprehensive and accurate outputs.
* **Streamlines workflows:** Automates tasks that would otherwise require human intervention.
* **Promotes creativity:** Sparks new ideas through diverse LLM interactions.