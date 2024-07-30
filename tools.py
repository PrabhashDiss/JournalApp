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

def view_entries_to(date):
    """View all journal entries up to a specific date."""
    command = ['jrnl', '-to', date]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    return result.stdout

def view_last_entries(number):
    """Display the last n journal entries."""
    command = ['jrnl', '-n', str(number)]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    return result.stdout

def view_entries_from_to(start_date, end_date):
    """View journal entries within a specific date range."""
    command = ['jrnl', '-from', start_date, '-to', end_date]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    return result.stdout

def view_entries_on(date):
    """Show journal entries for a specific date."""
    command = ['jrnl', '-on', date]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    return result.stdout

def search_entries(text):
    """Search journal entries containing specific text."""
    command = ['jrnl', '-contains', text]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    return result.stdout
