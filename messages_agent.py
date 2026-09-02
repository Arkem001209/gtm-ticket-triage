import os
import json
from anthropic import Anthropic

client = Anthropic(
    api_key=os.environ.get(
        "ANTHROPIC_API_KEY"
    ),
)

tools = [
    {
        "name": "lookup_account",
        "description": "search for accounts using dates and ID numbers",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticket_id": {"type": "string"},
                "received_at": {"type": "string", "format": "date-time"},
            },
            "required": ["received_at"],
        },
    }
    ]

messages = [
    {
        "role": "user",
        "content": f"look up the accoount IDs that were received on 2026-08-25 and return a list of ticket IDs "
    }
]

def run_tool(name, tool_input):
    if name == "lookup_account":
        return {"ticket_id": "T123", "received_at": tool_input["received_at"]}
    return {"error": f"Unknown tool: {name}"}

def main():
    print("Hello from gtm-ticket-triage!")


if __name__ == "__main__":
    main()
