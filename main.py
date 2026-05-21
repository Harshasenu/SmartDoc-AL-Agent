# Intelligent Document Assistant Agent

import ast
import glob
import math
import operator
import os
import time
from typing import Dict, List

from colorama import Fore, Style, init
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pypdf import PdfReader

# INITIAL SETUP

init(autoreset=True)
load_dotenv()

DOCUMENTS_DB: Dict[str, str] = {}

SUPPORTED_EXTENSIONS = ["*.txt", "*.pdf"]

# DOCUMENT LOADING

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from PDF safely.
    """
    text_content = []

    reader = PdfReader(file_path)

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text_content.append(page_text)

    return "\n".join(text_content)


def load_documents(directory_path: str = "documents") -> None:
    """
    Load all .txt and .pdf files into memory.
    """
    global DOCUMENTS_DB

    print(Fore.CYAN + "\n Scanning documents directory...\n")

    all_files: List[str] = []

    for extension in SUPPORTED_EXTENSIONS:
        search_pattern = os.path.join(directory_path, extension)
        all_files.extend(glob.glob(search_pattern))

    if not all_files:
        print(Fore.RED + " No supported documents found.")
        return

    for file_path in all_files:
        file_name = os.path.basename(file_path)

        try:
            if file_path.lower().endswith(".txt"):

                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()

            elif file_path.lower().endswith(".pdf"):

                content = extract_text_from_pdf(file_path)

            else:
                continue

            cleaned_content = " ".join(content.split())

            DOCUMENTS_DB[file_name] = cleaned_content

            print(Fore.GREEN + f" Indexed: {file_name}")

        except Exception as error:
            print(Fore.RED + f" Failed to load {file_name}: {error}")

    print(Fore.CYAN + f"\n Total documents loaded: {len(DOCUMENTS_DB)}")


# TOOL 1 — DOCUMENT QUERY TOOL

def query_document(document_name: str, query: str) -> str:
    """
    Search inside a specific document.
    """

    if document_name not in DOCUMENTS_DB:

        available_docs = ", ".join(DOCUMENTS_DB.keys())

        return (
            f"Document '{document_name}' not found.\n"
            f"Available documents: {available_docs}"
        )

    document_text = DOCUMENTS_DB[document_name]

    query_words = query.lower().split()

    sentences = document_text.split(".")

    matched_sentences = []

    for sentence in sentences:

        lowered_sentence = sentence.lower()

        if any(word in lowered_sentence for word in query_words):
            matched_sentences.append(sentence.strip())

    if not matched_sentences:
        return (
            "NO_MATCH_FOUND"
        )

    relevant_context = ". ".join(matched_sentences[:8])

    return (
        f"DOCUMENT: {document_name}\n"
        f"CONTENT:\n{relevant_context}"
    )


# TOOL 2 — SAFE CALCULATOR TOOL

ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def safe_eval(node):
    """
    Safely evaluate mathematical AST nodes.
    """

    if isinstance(node, ast.Num):
        return node.n

    elif isinstance(node, ast.BinOp):

        left = safe_eval(node.left)
        right = safe_eval(node.right)

        operator_function = ALLOWED_OPERATORS[type(node.op)]

        return operator_function(left, right)

    elif isinstance(node, ast.UnaryOp):

        operand = safe_eval(node.operand)

        operator_function = ALLOWED_OPERATORS[type(node.op)]

        return operator_function(operand)

    else:
        raise TypeError("Unsupported mathematical operation")


def calculate(expression: str) -> str:
    """
    Safely calculate mathematical expressions.
    """

    try:
        parsed_expression = ast.parse(expression, mode="eval")

        result = safe_eval(parsed_expression.body)

        return f"Calculation Result: {result}"

    except Exception as error:
        return f"Calculation Error: {error}"


# SYSTEM INSTRUCTIONS

def build_system_instruction() -> str:
    """
    Build strict grounding instructions.
    """

    available_documents = ", ".join(DOCUMENTS_DB.keys())

    return f"""
You are a deterministic document-bound AI assistant.

STRICT RULES:

1. You ONLY know information available inside the provided documents.

2. NEVER use external or pre-trained world knowledge.

3. Available documents:
{available_documents}

4. To answer factual questions:
   - ALWAYS use the query_document tool first.
   - NEVER guess or hallucinate.

5. If information is missing from documents:
   Reply EXACTLY:
   "I could not find this information in the provided documents"

6. If the user asks for calculations:
   - Use the calculate tool.
   - Never calculate mentally.

7. Every answer from a document MUST include:
   "Source: <document_name>"

8. Maintain conversation context:
   - Understand follow-up references like:
     "he", "she", "it", "that project", "those numbers"

9. Be concise, accurate, and deterministic.

10. Never fabricate citations.
"""


# AGENT SESSION

def initialize_agent():

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY not found inside environment variables."
        )

    client = genai.Client(api_key=api_key)

    return client


# ============================================================
# TERMINAL LOOP
# ============================================================

def start_terminal_assistant() -> None:
    """
    Start interactive AI terminal loop.
    """

    print(Fore.CYAN + "\n" + "=" * 60)
    print(Fore.CYAN + " SmartDoc AI ASSISTANT")
    print(Fore.CYAN + "=" * 60)

    if not DOCUMENTS_DB:

        print(Fore.RED + "\n No documents available.\n")
        return

    print(Fore.GREEN + "\n ...Documents indexed successfully.")

    print(Fore.YELLOW + "\nLoaded Documents:")

    for index, document_name in enumerate(DOCUMENTS_DB.keys(), start=1):
        print(Fore.YELLOW + f"{index}. {document_name}")

    print(Fore.CYAN + "\nYou can now ask questions.")
    print(Fore.CYAN + "Type 'exit' or 'quit' to end the session.")
    print(Fore.CYAN + "-" * 60)

    try:
        client = initialize_agent()

    except Exception as error:
        print(Fore.RED + f"\n Failed to initialize agent: {error}")
        return

    # Conversation memory
    conversation_history = ""

    while True:

        try:
            user_input = input(
                Fore.YELLOW + "\n User: "
            ).strip()

            if not user_input:
                continue

            # Exit conditions
            if user_input.lower() in ["exit", "quit"]:

                print(Fore.GREEN + "\n Session terminated successfully.\n")
                break

            

            # Send full conversation history to model
            # Add user message to memory
            conversation_history += f"\nUser: {user_input}"

            # Generate response
            response = client.models.generate_content(

                model="gemini-2.0-flash",

                contents=conversation_history,

                config=types.GenerateContentConfig(

                    system_instruction=build_system_instruction(),

                    tools=[
                        query_document,
                        calculate
                    ],

                    temperature=0.0,
                )
            )

            # Extract response text
            assistant_reply = response.text

            # Store assistant response in memory
            conversation_history += f"\nAssistant: {assistant_reply}"

            # Print response
            print(
                Fore.CYAN
                + "\n Assistant:\n"
                + Style.RESET_ALL
                + assistant_reply
            )

            print(Fore.CYAN + "-" * 60)

        except KeyboardInterrupt:

            print(Fore.GREEN + "\n\n Session interrupted safely.\n")
            break

        except Exception as error:

            error_message = str(error)

            # Handle Gemini API rate limits
            if "429" in error_message:

                print(
                    Fore.YELLOW
                    + "\n Gemini API rate limit reached."
                )

                print(
                    Fore.YELLOW
                    + " Waiting 60 seconds before retrying...\n"
                )

                time.sleep(60)

                continue

            # Handle all other errors
            print(
                Fore.RED
                + f"\n Runtime Error: {error}"
            )

# ============================================================
# MAIN ENTRYPOINT
# ============================================================

if __name__ == "__main__":

    load_documents("documents")

    start_terminal_assistant()