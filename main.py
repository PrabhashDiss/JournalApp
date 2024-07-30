from loguru import logger
from groq import Groq
from tools import *
import json
import gradio as gr

client = Groq(api_key="your-api-key")
MODEL = 'llama-3.1-70b-versatile'

def run_conversation(message, history):
    logger.info(f"Received message:\n{message}")
    logger.info(f"Received history:\n{history}")
    messages = [
        {
            "role": "system",
            "content": "You are a journal assistant. Use the relevant tools to manage your journal entries with correct grammar and punctuation.",
        }
    ]
    for history_message in history[-2:]:
        messages.append(
            {
                "role": "user",
                "content": history_message[0],
            }
        )
        messages.append(
            {
                "role": "system",
                "content": history_message[1],
            }
        )
    messages.append(
        {
            "role": "user",
            "content": message,
        }
    )
    tools = [
        {
            "type": "function",
            "function": {
                "name": "add_journal_entry",
                "description": "Add a journal entry",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "entry_text": {
                            "type": "string",
                            "description": "The text to add to the journal as a one-line entry",
                        }
                    },
                    "required": ["entry_text"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "view_all_entries",
                "description": "View all journal entries",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "view_entries_to",
                "description": "View all journal entries up to a specific date",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "date": {
                            "type": "string",
                            "description": "The end date in 'YYYY-MM-DD' format to view entries up to"
                        }
                    },
                    "required": ["date"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "view_last_entries",
                "description": "Display the last n journal entries",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "number": {
                            "type": "integer",
                            "description": "The number of recent entries to display"
                        }
                    },
                    "required": ["number"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "view_entries_from_to",
                "description": "View journal entries within a specific date range",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "start_date": {
                            "type": "string",
                            "description": "The start date of the range in 'YYYY-MM-DD' format"
                        },
                        "end_date": {
                            "type": "string",
                            "description": "The end date of the range in 'YYYY-MM-DD' format"
                        }
                    },
                    "required": ["start_date", "end_date"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "view_entries_on",
                "description": "Show journal entries for a specific date",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "date": {
                            "type": "string",
                            "description": "The date to view entries for in 'YYYY-MM-DD' format"
                        }
                    },
                    "required": ["date"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search_entries",
                "description": "Search journal entries containing specific text",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The text to search for within the journal entries"
                        }
                    },
                    "required": ["text"]
                }
            }
        }
    ]
    logger.info("Sending request to model with initial messages and tools.")
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        max_tokens=4096,
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    if tool_calls:
        available_functions = {
            "add_journal_entry": add_journal_entry,
            "view_all_entries": view_all_entries,
            "view_entries_to": view_entries_to,
            "view_last_entries": view_last_entries,
            "view_entries_from_to": view_entries_from_to,
            "view_entries_on": view_entries_on,
            "search_entries": search_entries
        }
        messages.append(response_message)
        logger.info("Processing tool calls from the model response.")
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            logger.info(f"Calling function '{function_name}' with arguments:\n{function_args}")
            function_response = function_to_call(**function_args)
            logger.info(f"Function '{function_name}' executed successfully. Response:\n{function_response}")
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,

                }
            )
        logger.info("Sending second request to model with updated messages.")
        messages.append(
            {
                "role": "user",
                "content": f"Give me the final response for the task ({message}) I requested.",
            }
        )
        second_response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
        )
        logger.info(f"Second response received. Response details:\n{second_response}")
        return second_response.choices[0].message.content
    else:
        logger.info("No tool calls found in the model response.")
        return response_message.content

iface = gr.ChatInterface(
    fn=run_conversation,
    title="Journal Assistant",
    description="Interact with your journal.",
)

iface.launch()
