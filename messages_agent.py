import json
import csv
from collections import defaultdict
from dotenv import load_dotenv
from anthropic import Anthropic
from pathlib import Path

load_dotenv()

client = Anthropic()
TICKETS_PATH = Path("data/tickets.csv")

file_object = client.files.upload(file=Path("data/tickets.csv"))

tools = [
    {
        "name": "lookup_account",
        "description": "Look up account tier, contract status, and support history for a customer by email address. Support history should include total number fo tickets and the 3 most recent ticket IDs. Use this before deciding ticket priority or routing. dont return any other details from the csv file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "email": {"type":"string", "description" : "senders email address from the ticket"}
            },
            "required": ["email"],
        },
    }
    ]

def lookup_account(email):
    with TICKETS_PATH.open(newline="") as f:
        rows = list(csv.DictReader(f))

    email = email.strip().lower()
    sender_rows = [r for r in rows if r["sender_email"].strip().lower() == email]
    if not sender_rows:
        return {"error": f"No account found for {email}"}

    account_name = sender_rows[0]["account_name"]
    tier = sender_rows[0]["account_tier"]

    account_rows = (
        [r for r in rows if r["account_name"] == account_name]
        if account_name
        else sender_rows
    )
    account_rows.sort(key=lambda r: r["received_at"], reverse=True)

    return {
        "account_name": account_name,
        "account_tier": tier,
        "account_status": "active", 
        "total_ticket_count": len(account_rows),
        "recent_ticket_ids": [r["ticket_id"] for r in account_rows[:3]],
    }

def run_tool(name, tool_input):
    if name == "lookup_account":
        return lookup_account(tool_input["email"])
    return {"error": f"Unknown tool: {name}"}

messages = [
    {
        "role": "user",
        "content": ("ticket received from tom.reilly@brightpath.org collect the account details for this account."),
    }
]

response = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=1024,
    tools=tools,
    tool_choice={"type": "auto", "disable_parallel_tool_use": True},
    messages=messages,
)

while response.stop_reason == "tool_use":
    tool_use = next(block for block in response.content if block.type == "tool_use")
    result = run_tool(tool_use.name, tool_use.input)

    messages.append({"role": "assistant", "content": response.content})
    messages.append(
        {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": json.dumps(result),
                }
            ],
        }
    )

    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1024,
        tools=tools,
        tool_choice={"type": "auto", "disable_parallel_tool_use": True},
        messages=messages,
    )

final_text = next(block for block in response.content if block.type == "text")
print(final_text.text)

#account tier, account status and support history

