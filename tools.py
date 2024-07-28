import subprocess

def current_date_time():
    """Get the current date and time."""
    command = ['date', '+%c']
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    return result.stdout

def add_journal_entry(entry_text, date_time=None):
    """Add a journal entry with optional date and time."""
    command = ['jrnl']

    if date_time:
        command.append(f"{date_time}: {entry_text}")
    else:
        command.append(entry_text)

    subprocess.run(command, check=True)

    return f"Journal entry added: {entry_text}"

def view_all_entries():
    """View all journal entries."""
    command = ['jrnl', '-to', 'today']

    result = subprocess.run(command, capture_output=True, text=True, check=True)
    return result.stdout
