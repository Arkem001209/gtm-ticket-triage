import json
from dotenv import load_dotenv
from anthropic import Anthropic
from pathlib import Path

load_dotenv()

client = Anthropic()

file_object = client.files.upload(file=Path("data/tickets.csv"))

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
    },
    {"type": "code_execution_20250825", "name": "code_execution"}
    ]
def run_tool(name, tool_input):
    if name == "lookup_account":
        return {"account_tier":"Enterprise", "account_status":"active","open_ticket_count": 23,"open_ticket_ids" : ["T001", "T002", "T003"]}
    return {"error": f"Unknown tool: {name}"}

messages = [
    {
        "role": "user",
        "content": [
            {"type":"text", "text":"ticket received from tom.reilly@brightpath.org collect the account details for this account from the csv file attached."},
            {"type":"container_upload", "file_id": file_object.id},
        ],
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

