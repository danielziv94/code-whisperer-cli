import pytest
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

# Add the parent directory to sys.path to allow imports from app/ and cli/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

# Conditional imports to allow patching before module loads in some tests
# We'll import `app` and `cli` where needed, usually after patching environment variables.
import requests # Needed for requests.exceptions in CLI tests
import httpx # For async FastAPI client testing
from click.testing import CliRunner # For testing Click CLI commands


# --- FastAPI Application Mocks (app/main.py dependencies) ---

@pytest.fixture
def mock_llm_chain() -> MagicMock:
    """
    Mocks the LangChain LLMChain instance.
    The `ainvoke` method is mocked to return a predefined value.

    Returns:
        MagicMock: A mock object for LLMChain.
    """
    mock_chain = MagicMock()
    mock_chain.ainvoke = AsyncMock(return_value={"text": "def hello_world():\n    return 'Hello, World!'\n"})
    return mock_chain

@pytest.fixture
def mock_openai_llm(mocker) -> MagicMock:
    """
    Mocks the langchain_openai.OpenAI class.
    Patches the class itself to return a mock LLM instance.

    Args:
        mocker: pytest-mock's mocker fixture.

    Returns:
        MagicMock: A mock object for the OpenAI LLM instance.
    """
    mock_llm = MagicMock()
    mocker.patch('langchain_openai.OpenAI', return_value=mock_llm)
    return mock_llm

@pytest.fixture
def mock_get_llm(mocker, mock_openai_llm) -> MagicMock:
    """
    Mocks the `get_llm` function within `app.main` to return a predefined mock LLM instance.
    This prevents actual LLM initialization and API key lookups during tests.

    Args:
        mocker: pytest-mock's mocker fixture.
        mock_openai_llm: The mock LLM instance to be returned.

    Returns:
        MagicMock: A mock object for the `get_llm` function.
    """
    return mocker.patch('app.main.get_llm', return_value=mock_openai_llm)

@pytest.fixture
def mock_llm_chain_init(mocker, mock_llm_chain) -> MagicMock:
    """
    Mocks the `LLMChain` constructor in `langchain.chains` to return our predefined mock chain.

    Args:
        mocker: pytest-mock's mocker fixture.
        mock_llm_chain: The mock LLMChain instance to be returned.

    Returns:
        MagicMock: A mock object for the `LLMChain` constructor.
    """
    return mocker.patch('langchain.chains.LLMChain', return_value=mock_llm_chain)


# --- FastAPI Application Tests (app/main.py) ---

@pytest.mark.asyncio
async def test_generate_code_success(mock_get_llm: MagicMock, mock_llm_chain_init: MagicMock, mocker) -> None:
    """
    Tests successful code generation through the FastAPI endpoint.
    Mocks the LLMChain's ainvoke method to return a predefined response.

    Args:
        mock_get_llm: Mock fixture for `get_llm`.
        mock_llm_chain_init: Mock fixture for `LLMChain` constructor.
        mocker: pytest-mock's mocker fixture.
    """
    # Patch environment variables before importing app.main to ensure OPENAI_API_KEY is set
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
        from app.main import app, CODE_PROMPT
        async with httpx.AsyncClient(app=app, base_url="http://test") as client:
            prompt_data = {"prompt": "python function that returns hello world", "language": "python"}
            response = await client.post("/generate", json=prompt_data)

            assert response.status_code == 200
            assert "code" in response.json()
            assert response.json()["code"] == "def hello_world():\n    return 'Hello, World!'"

            mock_get_llm.assert_called_once()
            mock_llm_chain_init.assert_called_once_with(llm=mock_get_llm.return_value, prompt=CODE_PROMPT)
            mock_llm_chain_init().ainvoke.assert_called_once_with(
                {"language": "python", "prompt": "python function that returns hello world"}
            )

@pytest.mark.asyncio
async def test_generate_code_empty_prompt_validation(mock_get_llm: MagicMock, mock_llm_chain_init: MagicMock) -> None:
    """
    Tests the FastAPI endpoint's input validation for an empty prompt.

    Args:
        mock_get_llm: Mock fixture for `get_llm`.
        mock_llm_chain_init: Mock fixture for `LLMChain` constructor.
    """
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
        from app.main import app
        async with httpx.AsyncClient(app=app, base_url="http://test") as client:
            prompt_data = {"prompt": "", "language": "python"}
            response = await client.post("/generate", json=prompt_data)

            assert response.status_code == 400
            assert "detail" in response.json()
            assert response.json()["detail"] == "Prompt cannot be empty."
            mock_get_llm.assert_not_called() # LLM should not be called for invalid input

@pytest.mark.asyncio
async def test_generate_code_llm_api_key_missing(mocker) -> None:
    """
    Tests the FastAPI endpoint's error handling when `OPENAI_API_KEY` is missing from environment variables.
    This test ensures `get_llm` raises an error if the key is not found.

    Args:
        mocker: pytest-mock's mocker fixture.
    """
    mocker.patch.dict(os.environ, {}, clear=True) # Clear env vars to simulate missing key
    # Delete app.main from sys.modules to force a full re-import and re-initialization of `llm` global
    if 'app.main' in sys.modules:
        del sys.modules['app.main']

    from app.main import app
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        prompt_data = {"prompt": "generate code", "language": "python"}
        response = await client.post("/generate", json=prompt_data)

        assert response.status_code == 500
        assert "detail" in response.json()
        assert "OPENAI_API_KEY not found" in response.json()["detail"]

@pytest.mark.asyncio
async def test_generate_code_llm_interaction_failure(mock_get_llm: MagicMock, mock_llm_chain_init: MagicMock) -> None:
    """
    Tests the FastAPI endpoint's error handling when the LLM interaction itself fails.
    Configures the mock LLMChain's `ainvoke` method to raise an exception.

    Args:
        mock_get_llm: Mock fixture for `get_llm`.
        mock_llm_chain_init: Mock fixture for `LLMChain` constructor.
    """
    mock_llm_chain_init().ainvoke.side_effect = Exception("LLM connection failed")

    with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
        from app.main import app
        async with httpx.AsyncClient(app=app, base_url="http://test") as client:
            prompt_data = {"prompt": "some prompt", "language": "python"}
            response = await client.post("/generate", json=prompt_data)

            assert response.status_code == 500
            assert "detail" in response.json()
            assert "Failed to generate code: LLM connection failed" in response.json()["detail"]


# --- CLI Application Tests (cli/commands.py) ---

@pytest.fixture
def runner() -> CliRunner:
    """
    Pytest fixture for Click CliRunner, used to invoke CLI commands in tests.

    Returns:
        CliRunner: An instance of Click's CliRunner.
    """
    return CliRunner()

@pytest.fixture
def mock_requests_post(mocker) -> MagicMock:
    """
    Mocks the `requests.post` function used by the CLI to interact with the FastAPI server.

    Args:
        mocker: pytest-mock's mocker fixture.

    Returns:
        MagicMock: A mock object for `requests.post`.
    """
    return mocker.patch('requests.post')

def test_cli_generate_success(runner: CliRunner, mock_requests_post: MagicMock) -> None:
    """
    Tests the CLI 'generate' command for successful code generation.
    Mocks the `requests.post` call to simulate a successful API response.

    Args:
        runner: Click CliRunner fixture.
        mock_requests_post: Mock fixture for `requests.post`.
    """
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"code": "print('Hello, CLI!')"}
    mock_response.raise_for_status.return_value = None # Ensure no exception for 2xx status
    mock_requests_post.return_value = mock_response

    # Patch environment variable for FastAPI URL if used in cli/commands.py
    with patch.dict(os.environ, {"CODE_WHISPERER_API_URL": "http://mock-api:8000"}):
        from cli.commands import cli
        result = runner.invoke(cli, ["generate", "print hello cli"])

        assert result.exit_code == 0
        assert "print('Hello, CLI!')" in result.output
        mock_requests_post.assert_called_once_with(
            "http://mock-api:8000/generate",
            json={"prompt": "print hello cli", "language": "python"}
        )

def test_cli_generate_with_language_option(runner: CliRunner, mock_requests_post: MagicMock) -> None:
    """
    Tests the CLI 'generate' command with a specific language option.

    Args:
        runner: Click CliRunner fixture.
        mock_requests_post: Mock fixture for `requests.post`.
    """
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"code": "<h1>Hello HTML</h1>"}
    mock_response.raise_for_status.return_value = None
    mock_requests_post.return_value = mock_response

    with patch.dict(os.environ, {"CODE_WHISPERER_API_URL": "http://mock-api:8000"}):
        from cli.commands import cli
        result = runner.invoke(cli, ["generate", "simple html heading", "--lang", "html"])

        assert result.exit_code == 0
        assert "<h1>Hello HTML</h1>" in result.output
        mock_requests_post.assert_called_once_with(
            "http://mock-api:8000/generate",
            json={"prompt": "simple html heading", "language": "html"}
        )

def test_cli_generate_empty_prompt_validation(runner: CliRunner, mock_requests_post: MagicMock) -> None:
    """
    Tests the CLI 'generate' command's handling of an empty prompt provided by the user.

    Args:
        runner: Click CliRunner fixture.
        mock_requests_post: Mock fixture for `requests.post`.
    """
    from cli.commands import cli
    result = runner.invoke(cli, ["generate", ""])

    assert result.exit_code != 0
    assert "Error: Prompt cannot be empty." in result.output
    mock_requests_post.assert_not_called()

def test_cli_generate_api_connection_error(runner: CliRunner, mock_requests_post: MagicMock) -> None:
    """
    Tests the CLI 'generate' command's error handling for API connection issues.
    Simulates a `requests.exceptions.ConnectionError`.

    Args:
        runner: Click CliRunner fixture.
        mock_requests_post: Mock fixture for `requests.post`.
    """
    mock_requests_post.side_effect = requests.exceptions.ConnectionError("Server not reachable")

    with patch.dict(os.environ, {"CODE_WHISPERER_API_URL": "http://mock-api:8000"}):
        from cli.commands import cli
        result = runner.invoke(cli, ["generate", "some prompt"])

        assert result.exit_code != 0
        assert "Error: Could not connect to the Code Whisperer API." in result.output
        mock_requests_post.assert_called_once()

def test_cli_generate_api_http_error(runner: CliRunner, mock_requests_post: MagicMock) -> None:
    """
    Tests the CLI 'generate' command's error handling for HTTP errors (e.g., 400 Bad Request) from the API.
    Simulates a `requests.exceptions.HTTPError` with a 400 status.

    Args:
        runner: Click CliRunner fixture.
        mock_requests_post: Mock fixture for `requests.post`.
    """
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"detail": "Prompt cannot be empty."}
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
    mock_requests_post.return_value = mock_response

    with patch.dict(os.environ, {"CODE_WHISPERER_API_URL": "http://mock-api:8000"}):
        from cli.commands import cli
        result = runner.invoke(cli, ["generate", "another prompt"])

        assert result.exit_code != 0
        assert "Error communicating with the API:" in result.output
        assert "API Error: Prompt cannot be empty." in result.output
        mock_requests_post.assert_called_once()

def test_cli_generate_api_internal_server_error(runner: CliRunner, mock_requests_post: MagicMock) -> None:
    """
    Tests the CLI 'generate' command's error handling for 500 Internal Server Errors from the API.
    Simulates a `requests.exceptions.HTTPError` with a 500 status.

    Args:
        runner: Click CliRunner fixture.
        mock_requests_post: Mock fixture for `requests.post`.
    """
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
    mock_requests_post.return_value = mock_response

    with patch.dict(os.environ, {"CODE_WHISPERER_API_URL": "http://mock-api:8000"}):
        from cli.commands import cli
        result = runner.invoke(cli, ["generate", "yet another prompt"])

        assert result.exit_code != 0
        assert "Error communicating with the API:" in result.output
        assert "API Error: 500 - Internal Server Error" in result.output
        mock_requests_post.assert_called_once()