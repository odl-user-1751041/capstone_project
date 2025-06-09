import os
import asyncio
import subprocess
from dotenv import load_dotenv

from semantic_kernel.kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai.services.azure_chat_completion import (
    AzureChatCompletion,
)
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.contents.utils.author_role import AuthorRole

# Load environment
load_dotenv()

# Set up Kernel
kernel = Kernel()
kernel.add_service(
    AzureChatCompletion(
        deployment_name=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
        endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    )
)

# Agent prompts
BA_PROMPT = (
    """You are a Business Analyst which will take the requirements from the user..."""
)
SE_PROMPT = """You are a Software Engineer..."""
PO_PROMPT = (
    """You are the Product Owner which will review the Software Engineer's code to ensure all user requirements are completed.
You are the guardian of quality. If the Software Engineer provides HTML code that:
1. Matches the user's original requirements, AND
2. Is properly wrapped in the format ```html ...code... ```, THEN
You must reply with ONLY the word: APPROVED.
If the requirements are not met, explain the defect and ask for a fix."""
)

# Create agents
business_analyst = ChatCompletionAgent(
    name="BusinessAnalyst", kernel=kernel, instructions=BA_PROMPT
)
software_engineer = ChatCompletionAgent(
    name="SoftwareEngineer", kernel=kernel, instructions=SE_PROMPT
)
product_owner = ChatCompletionAgent(
    name="ProductOwner", kernel=kernel, instructions=PO_PROMPT
)


# Helper to extract HTML code
def extract_html_code(history):
    for message in history:
        if message.role == AuthorRole.ASSISTANT and "```html" in message.content:
            start = message.content.find("```html") + len("```html")
            end = message.content.find("```", start)
            return message.content[start:end].strip()
    return None


# Main orchestrator
async def run_multi_agent(user_input: str):
    history = ChatHistory()
    history.add_message(ChatMessageContent(role=AuthorRole.USER, content=user_input))
    # history = [ChatMessageContent(role=AuthorRole.USER, content=user_input)]

    # Loop manually through agents
    agents = [business_analyst, software_engineer, product_owner]
    for _ in range(3):  # Max 3 rounds
        for agent in agents:
            reply = await agent.get_response(history)
            # history.append(reply)
            #history.add_message(
            #    ChatMessageContent(role=AuthorRole.ASSISTANT, content=reply.message)
            #)
            history.add_message(reply.message)
            print(f"\n[{agent.name}] says:\n{reply.content}")

            # Check for approval
            if "APPROVED" in reply.message.content.upper():
                html_code = extract_html_code(history)
                if html_code:
                    with open("index.html", "w", encoding="utf-8") as f:
                        f.write(html_code)
                    subprocess.run(["bash", "push_to_github.sh"])
                    print("\nHTML code saved and pushed to GitHub.")
                    return
    print("\n⚠️ No approval received after 3 rounds.")


# Run it
if __name__ == "__main__":
    user_prompt = input("Enter user request: ")
    asyncio.run(run_multi_agent(user_prompt))
