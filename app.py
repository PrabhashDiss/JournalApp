import json
import gradio as gr
from datetime import datetime
from gradio_client import Client

def load_entries():
    try:
        file_path = name.split()[0].lower() + "_journal.json"
        with open(file_path, "r") as file:
            entries = json.load(file)
    except FileNotFoundError:
        entries = {}
    return entries

def save_entries(entries):
    file_path = name.split()[0].lower() + "_journal.json"
    with open(file_path, "w") as file:
        json.dump(entries, file)

entries = {}

def display_entries():
    entries = load_entries()
    markdown = ""
    for entry in entries:
        markdown += f"## {entry}\n"
        for i, sub_entry in enumerate(entries[entry]):
            markdown += f"### {sub_entry['timestamp'].split()[1]}: {sub_entry['things_did']}\n\n"
    return markdown

def get_entries_for_date(date):
    if date in entries:
        return [(i, entry['things_did']) for i, entry in enumerate(entries[date])]
    else:
        return []

def refine_entry(entry):
    # Create the client instance
    client = Client("cemt/Phi-3-mini-4k-instruct")

    # Define the history for the conversation
    history = f'''
        You are here to help me write my journal entries.
        Rewrite the following entry to make it sound better in only one sentence.
        Entry:
        {entry}
    '''

    # Perform the prediction
    result = client.predict(
        message=entry,
        request=history,
        param_3=0.8,
        param_4=1024,
        param_5=40,
        param_6=1.1,
        param_7=0.95,
        api_name="/chat"
    )

    # Print the refined entry
    print(result)

    return result

def add_entry(original_entry):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    refined_entry = refine_entry(original_entry)
    today = datetime.now().strftime("%Y-%m-%d")
    entry = {"timestamp": timestamp, "things_did": refined_entry}
    if today in entries:
        entries[today].append(entry)
    else:
        entries[today] = [entry]
    save_entries(entries)
    return gr.update(value=display_entries()), gr.update(choices=list(entries.keys()), value=list(entries.keys())[-1] if entries else "No entries found."), gr.update(choices=[f"{index}. {value}" for index, value in get_entries_for_date(today)], value=f"{get_entries_for_date(today)[-1][0]}. {get_entries_for_date(today)[-1][1]}"), gr.update(choices=list(entries.keys()), value=list(entries.keys())[-1] if entries else "No entries found.")

def delete_entry(day, entry):
    index, value = entry.split(". ")
    del entries[day][int(index)]
    if not entries[day]:
        del entries[day]
    save_entries(entries)
    return gr.update(value=display_entries()), gr.update(choices=list(entries.keys()), value=list(entries.keys())[-1] if entries else "No entries found."), gr.update(choices=[f"{index}. {value}" for index, value in get_entries_for_date(day)], value=f"{get_entries_for_date(day)[-1][0]}. {get_entries_for_date(day)[-1][1]}" if get_entries_for_date(day) else "No entries found for selected date."), gr.update(choices=list(entries.keys()), value=list(entries.keys())[-1] if entries else "No entries found.")

def show_entries_by_date(date):
    if date in entries:
        entries_for_date = entries[date]
        return entries_for_date
    else:
        return "No entries found for selected date."

def ask_question(question):
    # Create the client instance
    client = Client("cemt/Phi-3-mini-4k-instruct")

    # Define the history for the conversation
    history = f'''
        You are here to help me answer my question about my journal entries.
        Journal Entries:
        {display_entries()}
        Question:
        {question}
    '''

    # Perform the prediction
    result = client.predict(
        message=question,
        request=history,
        param_3=0.8,
        param_4=1024,
        param_5=40,
        param_6=1.1,
        param_7=0.95,
        api_name="/chat"
    )

    # Print the answer
    print(result)

    return gr.update(value=result)

def update_entry_dropdown(date):
    return gr.update(choices=[f"{index}. {value}" for index, value in get_entries_for_date(date)], value=f"{get_entries_for_date(date)[-1][0]}. {get_entries_for_date(date)[-1][1]}")
def main_interface():
    with gr.Blocks() as app:
        with gr.Row():
            with gr.Column():
                gr.Markdown("# Entries")
                entries_markdown = gr.Markdown(value=display_entries())
            with gr.Column():
                gr.Markdown("# Add Entry")
                entry_text = gr.Textbox(lines=5, placeholder="Write your journal entry here...")
                add_button = gr.Button("Add Entry")
                gr.Markdown("# Delete Entry")
                date_dropdown_delete = gr.Dropdown(label="Select Date", choices=list(entries.keys()), value=list(entries.keys())[-1] if entries else "No entries found.")
                entry_dropdown = gr.Dropdown(label="Select Entry", choices=[f"{index}. {value}" for index, value in get_entries_for_date(date_dropdown_delete.value)], value=f"{get_entries_for_date(date_dropdown_delete.value)[-1][0]}. {get_entries_for_date(date_dropdown_delete.value)[-1][1]}" if get_entries_for_date(date_dropdown_delete.value) else "No entries found for selected date.")
                delete_button = gr.Button("Delete Entry")
            with gr.Column():
                gr.Markdown("# Summary of Entries by Date", visible=False)
                date_dropdown_show = gr.Dropdown(label="Select Date", choices=list(entries.keys()), value=list(entries.keys())[-1] if entries else "No entries found.", visible=False)
                show_button = gr.Button("Summarize Entries for Selected Date", visible=False)
                selected_entries = gr.Markdown("", visible=False)
                gr.Markdown("# Ask Questions")
                question_text = gr.Textbox(lines=5, placeholder="Ask a question about your journal entries...")
                ask_button = gr.Button("Ask")
                answer_markdown = gr.Markdown(value="")
        add_button.click(fn=add_entry, inputs=entry_text, outputs=[entries_markdown, date_dropdown_delete, entry_dropdown, date_dropdown_show])
        delete_button.click(fn=delete_entry, inputs=[date_dropdown_delete, entry_dropdown], outputs=[entries_markdown, date_dropdown_delete, entry_dropdown, date_dropdown_show])
        show_button.click(fn=show_entries_by_date, inputs=date_dropdown_show, outputs=selected_entries)
        ask_button.click(fn=ask_question, inputs=question_text, outputs=answer_markdown)
        date_dropdown_delete.change(update_entry_dropdown, inputs=date_dropdown_delete, outputs=entry_dropdown)

    return app

name = ""
def show_main_interface(profile: gr.OAuthProfile | None):
    if profile is None:
        with gr.Blocks() as app:
            gr.Markdown("Please log in to continue.")
        return app
    name = profile.name
    return main_interface()

if __name__ == "__main__":
    with gr.Blocks() as demo:
        gr.LoginButton()

        demo.load(show_main_interface, inputs=None, outputs=gr.Blocks())

    demo.launch()
