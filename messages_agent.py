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
        "description": "Look up account tier, contract status, and support history for a customer by email address. Support history should include total number fo tickets and the 3 most recent ticket IDs. Use this before deciding ticket priority or routing.",
        "input_schema": {
            "type": "object",
            "properties": {
                "email": {"type":"string", "description" : "senders email address from the ticket"}
            },
            "required": ["email"],
        },
    }
    ]

messages = [
    {
        "role": "user",
        "content": "ticket received from tom.reilly@brightpath.org"
    }
]

response = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=1024,
    tools=tools,
    tool_choice={"type": "auto", "disable_parallel_tool_use": True},
    messages=messages,
)

def run_tool(name, tool_input):
    if name == "lookup_account":
        return {"account_tier":"Enterprise", "account_status":"active","open_ticket_count": 23,"open_ticket_ids" : ["T001", "T002", "T003"] , "received_at": tool_input["received_at"]}
    return {"error": f"Unknown tool: {name}"}

#account tier, account status and support history

