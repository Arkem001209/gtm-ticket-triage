import json
import csv
from dotenv import load_dotenv
from anthropic import Anthropic
from pathlib import Path

load_dotenv()

client = Anthropic()
TICKETS_PATH = Path("data/tickets.csv")


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
    },
    {
        "name": "create_task",
        "description": "Use the notes value of the account lookup to create a task based on your previous triage result summary for action by future agents",
        "input_schema": {
            "type": "object",
            "properties": {
                "account_name": {"type":"string", "description" : "the account name field from lookup_account"},
                "account_tier": {"type":"string", "description" : "the account tier derived from the lookup_account call"},
                "notes": {"type":"string", "description" : "Details of the ticket sent from a client detailing the issue or request received from lookup_account"}
            },
            "required": ["email", "account_tier","notes"],
        },
    },
    {
        #TO DO - DEFINE ESCALATE TO HUMAN BEFORE RUNNING AGAIN
        "name": "escalate_to_human",
        "description": "If the confidence score is below 0.5 use this tool to respond to the user that a human operator will be in touch",
        "input_schema": {
            "type": "object",
            "properties": {
                "confidence_score": {"type":"float", "description" : "score from 0.0 to 10.0 on how confident the agent is "}
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
        "content": ("triage the ticket received from tom.reilly@brightpath.org. collect the account details for this account, decide on "),
    }
]

response = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=1024,
    tools=tools,
    tool_choice={"type": "auto", "disable_parallel_tool_use": True},
    system="""

    You are a GTM support ticket triage agent. Your job is to receive requests from the user and triage them based on the account details you can get by using lookup_account. 
    you should read the subject, and support ticket content and lookup the account using the lookup_account tool to gather as much information as possible. Then, create a confidence score on the context of the information you have.

    The confidence score. a float range of 0.0 to 10.0

    9.0 + = ticket and account unambiguously fit one category beyond reasonable doubt
    0.51 to 9.0 means you are reasonably confident in the categorisation of the ticket and can handle the request while needing to clear up some details
    0 to 0.5 means that major details are missing and context contradicts itself. If the score is this low you should escalate to a human using the appropriate tool.

    """,
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

