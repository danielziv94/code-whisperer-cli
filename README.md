# Code Whisperer CLI

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/danielziv94/code-whisperer-cli/actions)
[![Stars](https://img.shields.io/github/stars/danielziv94/code-whisperer-cli?style=social)](https://github.com/danielziv94/code-whisperer-cli/stargazers)

## Description
The Code Whisperer CLI is an innovative command-line interface tool designed to supercharge developer productivity. Leveraging the power of large language models (LLMs), it generates concise and accurate code snippets in various programming languages based on natural language prompts. This utility acts as an intelligent developer assistant, significantly reducing cognitive load by quickly providing boilerplate code, recalling specific syntax, or offering architectural patterns, allowing developers to focus on core logic and problem-solving.

In an era where AI for developer productivity is a paramount trend, the Code Whisperer CLI stands out as an efficient, intuitive, and highly valuable utility. It streamlines development workflows by bringing the capabilities of advanced AI directly to your terminal.

## Features
-   **Natural Language to Code:** Translate plain English descriptions into functional code snippets.
-   **Python Function Generation:** Instantly generate Python functions for common tasks (e.g., file I/O, data manipulation).
-   **Web Framework Boilerplate:** Quickly scaffold basic structures for web development (e.g., FastAPI endpoint definitions).
-   **Frontend Snippets:** Generate fundamental HTML boilerplate or specific UI components.
-   **Syntax Recall:** A rapid reference for language-specific syntax or patterns.

## Tech Stack
-   **Python:** The core programming language.
-   **Click:** A robust and user-friendly library for creating command-line interfaces.
-   **FastAPI:** A modern, fast (high-performance) web framework for building APIs, used here to serve as a local server for LLM interaction.
-   **LangChain:** A framework for developing applications powered by language models, facilitating complex prompt engineering and interaction.
-   **OpenAI API (or similar LLM provider):** The underlying Large Language Model providing the intelligence.

## Installation
To get Code Whisperer CLI up and running on your local machine, follow these steps:

1.  **Clone the repository:**
    bash
    git clone https://github.com/danielziv94/code-whisperer-cli.git
    cd code-whisperer-cli
    
2.  **Create and activate a virtual environment:**
    It's highly recommended to use a virtual environment to manage dependencies.
    bash
    python -m venv venv
    # On macOS/Linux:
    source venv/bin/activate
    # On Windows:
    .\venv\Scripts\activate
    
3.  **Install dependencies:**
    bash
    pip install -r requirements.txt
    
4.  **Configure Environment Variables:**
    Create a `.env` file in the project root directory and add your LLM API key.
    For OpenAI, it would look like this:
        OPENAI_API_KEY="your_openai_api_key_here"
        *Replace `"your_openai_api_key_here"` with your actual API key.*

## Usage
To use the Code Whisperer CLI, you'll first need to start the local FastAPI server that handles LLM interactions, and then use the `whisper` command in a separate terminal.

1.  **Start the FastAPI Server:**
    Open your first terminal, navigate to the project root, activate your virtual environment, and run the FastAPI application:
    bash
    cd app
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
        You should see output indicating the server is running, typically on `http://127.0.0.1:8000`.

2.  **Use the Code Whisperer CLI:**
    Open a *second* terminal, navigate to the project root, activate your virtual environment, and use the `whisper` command followed by the desired language/framework and your natural language prompt.

    **General Syntax:**
    bash
    whisper <language_or_framework> "<your natural language prompt>"
    
    **Examples:**

    *   **Generate a Python function for file I/O:**
        bash
        whisper python "create a function that reads a text file line by line and returns a list of strings"
        
    *   **Generate a basic FastAPI endpoint structure:**
        bash
        whisper fastapi "generate a simple GET endpoint at /items that returns a list of dictionaries"
        
    *   **Generate simple HTML boilerplate:**
        bash
        whisper html "generate a basic html5 boilerplate with a title 'My Awesome Page' and a heading 'Welcome'"
        
    The generated code will be printed directly to your terminal.

## Contributing
We welcome contributions to the Code Whisperer CLI! If you'd like to improve the tool, add new features, or fix bugs, please follow these guidelines:

1.  **Fork the repository:** Start by forking the `code-whisperer-cli` repository to your GitHub account.
2.  **Clone your fork:**
    bash
    git clone https://github.com/danielziv94/code-whisperer-cli.git
    cd code-whisperer-cli
    3.  **Create a new branch:**
    bash
    git checkout -b feature/your-feature-name
        or
    bash
    git checkout -b bugfix/issue-description
    4.  **Make your changes:** Implement your feature or bug fix.
5.  **Test your changes:** Ensure your changes don't break existing functionality and ideally add new tests.
6.  **Commit your changes:** Write clear and concise commit messages.
    bash
    git commit -m "feat: Add new command for JavaScript snippets"
    7.  **Push to your fork:**
    bash
    git push origin feature/your-feature-name
    8.  **Open a Pull Request:** Go to the original `code-whisperer-cli` repository on GitHub and open a new pull request from your forked branch. Provide a detailed description of your changes.

Please ensure your code adheres to good practices and maintainability.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

MIT License

Copyright (c) 2026 Daniel Ziv

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
