import json
from tkinter import *
from datetime import datetime

def load_entries():
    try:
        with open("journal.json", "r") as file:
            entries = json.load(file)
    except FileNotFoundError:
        entries = {}
    return entries

def save_entries(entries):
    with open("journal.json", "w") as file:
        json.dump(entries, file)

def add_entry():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    things_did = entry_text.get(1.0, END).strip()
    today = datetime.now().strftime("%Y-%m-%d")
    entry = {"timestamp": timestamp, "things_did": things_did}
    if today in entries:
        entries[today].append(entry)
    else:
        entries[today] = [entry]
    save_entries(entries)
    entry_text.delete(1.0, END)
    status_label.config(text="Entry added successfully.")
    display_entries()

def delete_entry(day, index):
    if day in entries and 0 <= index < len(entries[day]):
        del entries[day][index]
        save_entries(entries)
        status_label.config(text="Entry deleted successfully.")
        display_entries()
    else:
        status_label.config(text="Invalid index.")

def display_entries():
    for widget in window.winfo_children():
        widget.destroy()
    
    add_button = Button(window, text="Add Entry", command=add_entry)
    add_button.pack(side="top", padx=10, pady=5)

    global entry_text
    entry_text = Text(window, height=5, width=50)
    entry_text.pack(side="top", padx=10, pady=5, fill="both", expand=True)

    global status_label
    status_label = Label(window, text="")
    status_label.pack(side="top", padx=10, pady=5)

    for day, day_entries in entries.items():
        date_label = Label(window, text=f"--- {day} ---")
        date_label.pack(anchor="w", padx=10, pady=(5, 0))

        for i, entry in enumerate(day_entries):
            entry_frame = Frame(window)
            entry_frame.pack(anchor="w", padx=30, pady=(0, 5), fill="x")

            timestamp_label = Label(entry_frame, text=f"Timestamp: {entry['timestamp']}")
            timestamp_label.pack(side="left")

            things_did_label = Label(entry_frame, text=f"Things you did: {entry['things_did']}")
            things_did_label.pack(side="left")

            delete_button = Button(entry_frame, text="Delete", command=lambda d=day, index=i: delete_entry(d, index))
            delete_button.pack(side="right")

def main():
    global entries
    entries = load_entries()

    global window
    window = Tk()
    window.title("Journal Application")

    display_entries()

    window.mainloop()

if __name__ == "__main__":
    main()
