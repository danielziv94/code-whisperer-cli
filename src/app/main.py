import os
from contextlib import asynccontextmanager
from typing import Dict, Any
import time
from collections import defaultdict
import asyncio

import uvicorn
from fastapi import FastAPI, HTTPException, Request, status
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import fastapi

load_dotenv()

OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set.")

llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model="gpt-4o-mini", temperature=0.7)

code_generation_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are an expert code whisperer. Generate only the code requested by the user, without any additional explanations or markdown code block fences. Focus on generating clean, runnable code. Provide only the code, no prose."),
        ("user", "{prompt}")
    ]
)
code_generation_chain = code_generation_template | llm | StrOutputParser()

RATE_LIMIT_PER_MINUTE: int = 5
requests_per_minute: Dict[str, Dict[int, int]] = defaultdict(lambda: defaultdict(int))
rate_limit_lock = asyncio.Lock()

async def check_rate_limit(request: Request) -> None:
    """
    Checks the rate limit for the client IP.
    """
    client_ip: str = request.client.host if request.client else "unknown"
    current_minute: int = int(time.time() / 60)

    async with rate_limit_lock:
        for minute in list(requests_per_minute[client_ip].keys()):
            if minute < current_minute - 1:
                del requests_per_minute[client_ip][minute]

        requests_per_minute[client_ip][current_minute] += 1
        request_count: int = sum(requests_per_minute[client_ip].values())

        if request_count > RATE_LIMIT_PER_MINUTE:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI application lifespan context manager.
    """
    print("Code Whisperer FastAPI app starting up...")
    yield
    print("Code Whisperer FastAPI app shutting down.")

app = FastAPI(
    title="Code Whisperer API",
    description="API for generating code snippets using an LLM.",
    version="0.1.0",
    lifespan=lifespan
)

class CodeRequest(BaseModel):
    """
    Request model for code generation.
    """
    prompt: str = Field(..., min_length=1, description="Natural language prompt for code generation.")

@app.get("/")
async def read_root() -> Dict[str, str]:
    """
    Root endpoint for health check.
    """
    return {"message": "Code Whisperer API is running!"}

@app.post("/generate", dependencies=[fastapi.Depends(check_rate_limit)])
async def generate_code(request_body: CodeRequest) -> Dict[str, str]:
    """
    Generates code snippets based on a natural language prompt using an LLM.

    Args:
        request_body: A CodeRequest object containing the prompt.

    Returns:
        A dictionary with the generated code string.

    Raises:
        HTTPException: If the prompt is empty or an error occurs during code generation.
    """
    if not request_body.prompt.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prompt cannot be empty."
        )

    try:
        generated_code: str = await code_generation_chain.ainvoke({"prompt": request_body.prompt})
        return {"code": generated_code}
    except Exception as e:
        print(f"Error during code generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate code: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
