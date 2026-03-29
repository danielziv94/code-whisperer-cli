import json
import os
import sys
from http import HTTPStatus
from typing import Optional, Dict, Any

import click
import requests

API_BASE_URL: str = os.getenv("CODE_WHISPERER_API_URL", "http://localhost:8000")

def _call_api(endpoint: str, prompt: str) -> Optional[Dict[str, Any]]:
    """
    Internal helper function to call the Code Whisperer API.

    Args:
        endpoint: The API endpoint to call (e.g., "/generate").
        prompt: The natural language prompt to send to the API.

    Returns:
        A dictionary containing the API response, or None if an error occurred.
    """
    response = None
    try:
        response = requests.post(
            f"{API_BASE_URL}{endpoint}",
            json={"prompt": prompt},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        click.echo(
            click.style(
                f"Error: Could not connect to the Code Whisperer API server at {API_BASE_URL}.\n"
                "Please ensure the FastAPI application (src/app/main.py) is running.",
                fg="red"
            ),
            err=True
        )
        return None
    except requests.exceptions.Timeout:
        click.echo(
            click.style("Error: The API request timed out. The LLM might be taking too long.", fg="red"),
            err=True
        )
        return None
    except requests.exceptions.RequestException as e:
        if response is not None:
            try:
                error_detail = response.json().get("detail", str(e))
            except json.JSONDecodeError:
                error_detail = response.text
            click.echo(
                click.style(f"API Error ({response.status_code}): {error_detail}", fg="red"),
                err=True
            )
        else:
            click.echo(click.style(f"An unexpected request error occurred: {e}", fg="red"), err=True)
        return None
    except json.JSONDecodeError:
        click.echo(
            click.style(f"Error: Could not parse JSON response from API: {response.text}", fg="red"),
            err=True
        )
        return None


@click.group()
def cli() -> None:
    """
    Code Whisperer CLI: Your AI assistant for quick code snippets.
    """
    pass

@cli.command("python-file-io")
@click.option(
    "--description",
    "-d",
    type=str,
    default="read and write a text file",
    help="Describe the file I/O operation (e.g., 'read a CSV', 'write to a binary file')."
)
def python_file_io(description: str) -> None:
    """
    Generates a Python function for file I/O operations.
    """
    prompt: str = (
        f"Generate a Python function that {description}. "
        "Include type hints and a basic docstring. The function should take a file path as an argument."
    )
    click.echo(f"Generating Python file I/O function for: '{description}'...")
    response_data: Optional[Dict[str, Any]] = _call_api("/generate", prompt)

    if response_data and "code" in response_data:
        click.echo("\n" + click.style("Generated Python Code:", fg="green"))
        click.echo(response_data["code"])
    else:
        click.echo(click.style("Failed to generate Python file I/O code.", fg="red"), err=True)
        sys.exit(1)

@cli.command("fastapi-endpoint")
@click.option(
    "--name",
    "-n",
    type=str,
    required=True,
    help="Name of the FastAPI endpoint function (e.g., 'create_item')."
)
@click.option(
    "--method",
    "-m",
    type=click.Choice(["GET", "POST", "PUT", "DELETE"], case_sensitive=False),
    default="GET",
    help="HTTP method for the endpoint."
)
@click.option(
    "--path",
    "-p",
    type=str,
    default="/items",
    help="URL path for the endpoint (e.g., '/users/{user_id}')."
)
@click.option(
    "--description",
    "-d",
    type=str,
    default="",
    help="Additional description for the endpoint functionality."
)
def fastapi_endpoint(name: str, method: str, path: str, description: str) -> None:
    """
    Generates a basic FastAPI endpoint structure.
    """
    prompt_parts: list[str] = [
        f"Generate a basic FastAPI endpoint using the {method} method at path '{path}'.",
        f"The function should be named '{name}'.",
        "Include type hints, a Pydantic request body model if applicable for POST/PUT, and a Google-style docstring.",
    ]
    if description:
        prompt_parts.append(f"Its functionality is: {description}.")
    
    prompt: str = " ".join(prompt_parts)
    click.echo(f"Generating FastAPI {method} endpoint '{name}' at '{path}'...")
    response_data: Optional[Dict[str, Any]] = _call_api("/generate", prompt)

    if response_data and "code" in response_data:
        click.echo("\n" + click.style("Generated FastAPI Endpoint Code:", fg="green"))
        click.echo(response_data["code"])
    else:
        click.echo(click.style("Failed to generate FastAPI endpoint code.", fg="red"), err=True)
        sys.exit(1)

@cli.command("html-boilerplate")
@click.option(
    "--title",
    "-t",
    type=str,
    default="My Web Page",
    help="Title for the HTML document."
)
@click.option(
    "--lang",
    "-l",
    type=str,
    default="en",
    help="Language attribute for the HTML document (e.g., 'en', 'es', 'fr')."
)
@click.option(
    "--add-css",
    is_flag=True,
    help="Include a basic internal CSS style block."
)
@click.option(
    "--add-js",
    is_flag=True,
    help="Include a basic internal JavaScript script block."
)
def html_boilerplate(title: str, lang: str, add_css: bool, add_js: bool) -> None:
    """
    Generates simple HTML5 boilerplate.
    """
    prompt_parts: list[str] = [
        f"Generate a simple HTML5 boilerplate with the title '{title}' and language '{lang}'.",
        "Include common meta tags (charset, viewport, compatibility).",
    ]
    if add_css:
        prompt_parts.append("Add a basic internal CSS style block in the <head>.")
    if add_js:
        prompt_parts.append("Add a basic internal JavaScript script block before the closing </body> tag.")

    prompt: str = " ".join(prompt_parts)
    click.echo(f"Generating HTML5 boilerplate for '{title}' (lang='{lang}')...")
    response_data: Optional[Dict[str, Any]] = _call_api("/generate", prompt)

    if response_data and "code" in response_data:
        click.echo("\n" + click.style("Generated HTML Code:", fg="green"))
        click.echo(response_data["code"])
    else:
        click.echo(click.style("Failed to generate HTML boilerplate.", fg="red"), err=True)
        sys.exit(1)

if __name__ == "__main__":
    cli()
