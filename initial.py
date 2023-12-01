import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from github import Github, GithubException, BadCredentialsException
from datetime import datetime, timedelta 
import pytz
import threading
import schedule
import time
##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

# Create a global variable for the GitHub object
g = None
file_content = None  # Define file_content as a global variable
filename = None  # Define filename as a global variable

def fetch_repos():
    username = username_entry.get()

    try:
        global g  # Use the global GitHub object
        token = token_entry.get()
        g = Github(token)
        user = g.get_user(username)
        repos = [repo.name for repo in user.get_repos()]
        repo_combobox['values'] = sorted(repos)
    except Exception as e:
        messagebox.showerror("Error", f"Error fetching repos: {str(e)}")

def browse_repository():
    selected_repo = repo_combobox.get()

    try:
        user = g.get_user(username_entry.get())
        repo = user.get_repo(selected_repo)
        contents = repo.get_contents('')

        file_list = []
        folder_list = []

        for content in contents:
            if content.type == 'dir':
                folder_list.append(content.name)
            else:
                file_list.append(content.name)

        populate_tree(file_list, folder_list)
    except Exception as e:
        messagebox.showerror("Error", f"Error browsing repository: {str(e)}")

def create_and_commit_file(filename):
    content = file_content.get("1.0", "end-1c")
    selected_repo = repo_combobox.get()
    try:
        user = g.get_user(username_entry.get())
        repo = user.get_repo(selected_repo)
        repo.create_file(filename, f"Create {filename}", content)
        messagebox.showinfo("File Created", f"File '{filename}' created successfully and committed.")
        browse_repository()
    except Exception as e:
        messagebox.showerror("Error", f"Error creating file and committing: {str(e)}")

def create_file_gui(filename):
    create_file_window = tk.Toplevel(app)
    create_file_window.title("Create File")
    
    global file_content  # Access the global file_content variable
    file_content = tk.Text(create_file_window, wrap=tk.WORD, height=10, width=40)
    file_content.pack()
    
    file_content_label = tk.Label(create_file_window, text="File Content:")
    file_content_label.pack()
    
    commit_button = tk.Button(create_file_window, text="Commit Now", command=lambda: create_and_commit_file(filename))
    commit_button.pack()
    
    schedule_commit_button = tk.Button(create_file_window, text="Schedule Commit", command=lambda: schedule_commit_dialog(filename))
    schedule_commit_button.pack()

def schedule_commit_dialog(filename):
    schedule_commit_window = tk.Toplevel(app)
    schedule_commit_window.title("Schedule Commit")
    
    # Add widgets for date, time, and timezone selection
    date_label = tk.Label(schedule_commit_window, text="Commit Date (YYYY-MM-DD):")
    date_label.pack()
    date_var = tk.StringVar()
    date_entry = tk.Entry(schedule_commit_window, textvariable=date_var)
    date_entry.pack()
    
    time_label = tk.Label(schedule_commit_window, text="Commit Time (HH:MM):")
    time_label.pack()
    time_var = tk.StringVar()
    time_entry = tk.Entry(schedule_commit_window, textvariable=time_var)
    time_entry.pack()
    
    timezone_label = tk.Label(schedule_commit_window, text="Timezone:")
    timezone_label.pack()
    timezone_var = tk.StringVar()
    timezone_combobox = ttk.Combobox(schedule_commit_window, textvariable=timezone_var)
    timezone_combobox['values'] = pytz.all_timezones
    timezone_combobox.pack()

    # Add a button to schedule the commit
    schedule_button = tk.Button(schedule_commit_window, text="Schedule Commit", command=lambda: schedule_commit(filename, date_var.get(), time_var.get(), timezone_var.get()))
    schedule_button.pack()

def schedule_commit_dialog(filename):
    schedule_commit_window = tk.Toplevel(app)
    schedule_commit_window.title("Schedule Commit")
    
    # Add widgets for date, time, and timezone selection
    date_label = tk.Label(schedule_commit_window, text="Commit Date (YYYY-MM-DD):")
    date_label.pack()
    date_var = tk.StringVar()
    date_entry = tk.Entry(schedule_commit_window, textvariable=date_var)
    date_entry.pack()
    
    time_label = tk.Label(schedule_commit_window, text="Commit Time (HH:MM):")
    time_label.pack()
    time_var = tk.StringVar()
    time_entry = tk.Entry(schedule_commit_window, textvariable=time_var)
    time_entry.pack()
    
    timezone_label = tk.Label(schedule_commit_window, text="Timezone:")
    timezone_label.pack()
    timezone_var = tk.StringVar()
    timezone_combobox = ttk.Combobox(schedule_commit_window, textvariable=timezone_var)
    timezone_combobox['values'] = pytz.all_timezones
    timezone_combobox.pack()

    # Add a button to schedule the commit
    schedule_button = tk.Button(schedule_commit_window, text="Schedule Commit", command=lambda: schedule_commit(filename, date_var.get(), time_var.get(), timezone_var.get(), schedule_commit_window))
    schedule_button.pack()

def schedule_commit(filename, commit_date, commit_time, commit_timezone, window):
    # Your code for scheduling the commit goes here
    # Convert date, time, and timezone to a datetime object and schedule the commit
    try:
        user = g.get_user(username_entry.get())
        selected_repo = repo_combobox.get()
        repo = user.get_repo(selected_repo)

        # Convert the selected date, time, and timezone to a datetime object
        commit_datetime = datetime.strptime(f"{commit_date} {commit_time}", "%Y-%m-%d %H:%M")
        commit_datetime = pytz.timezone(commit_timezone).localize(commit_datetime)

        # Calculate the delay in seconds until the scheduled commit
        current_datetime = datetime.now(pytz.utc)
        delay_seconds = (commit_datetime - current_datetime).total_seconds()

        # Ensure the commit is scheduled at least 1 minute in the future
        if delay_seconds < 60:
            messagebox.showerror("Error", "Please schedule the commit at least 1 minute in the future.")
            return

        # Schedule the commit using the GitHub API
        content = file_content.get("1.0", "end-1c")  # Access file content
        scheduled_datetime_utc = current_datetime + timedelta(seconds=delay_seconds)
        repo.create_file(filename, f"Create {filename}", content, scheduled_datetime_utc)
        messagebox.showinfo("Commit Scheduled", f"Commit scheduled for {scheduled_datetime_utc} UTC.")
        window.destroy()

    except BadCredentialsException as bce:
        print("Bad credentials error:", str(bce))
        messagebox.showerror("Error", "Bad credentials. Please check your access token.")
    except GithubException as ge:
        print("GitHub API error:", str(ge))
        messagebox.showerror("Error", f"GitHub API error: {str(ge)}")
    except Exception as e:
        print("Error scheduling commit:", str(e))  # Print the error details
        messagebox.showerror("Error", f"Error scheduling commit: {str(e)}")


# Define the populate_tree function
def populate_tree(files, folders):
    file_tree.delete(*file_tree.get_children())
    for folder in folders:
        file_tree.insert("", "end", text=folder, values=("folder", ""))
    for file in files:
        file_tree.insert("", "end", text=file, values=("file", file))

def on_search_entry_change(*args):
    search_text = search_var.get()
    filtered_repos = [repo for repo in repo_combobox['values'] if search_text.lower() in repo.lower()]
    repo_combobox['values'] = sorted(filtered_repos)

# Create a custom Combobox widget with autocomplete feature
class AutocompleteCombobox(ttk.Combobox):
    def set_completion_list(self, completion_list):
        self._completion_list = sorted(completion_list)
        self._hits = []
        self.position = 0
        self._hits = self._completion_list[:]
        self.position = 0
        self.max_show = 10
        self.show_popup = False
        self.bind('<KeyRelease>', self.handle_keyrelease)
        self['values'] = self._hits

    def autocomplete(self, delta=0):
        if delta:
            self.delete(self.index(tk.INSERT), tk.END)
        _hits = []
        _hits = [item for item in self._completion_list if self.matches(item)]
        if _hits != self._hits:
            self._hit_index = 0
            self._hits = _hits
        if _hits == self._hits and self._hits:
            self._hit_index = (self._hit_index + delta) % len(_hits)
        if _hits != self._hits and _hits:
            self._hit_index = 0
            self._hits = _hits
        if _hits:
            _hits = _hits[self._hit_index]
        if _hits:
            self.delete(0, tk.END)
            self.insert(0, _hits)
            self.select_range(self.position, tk.END)

    def handle_keyrelease(self, event):
        if event.keysym in ('Up', 'Down', 'Shift_R', 'Shift_L', 'Control_R', 'Control_L', 'Alt_R', 'Alt_L'):
            return
        if event.keysym == 'BackSpace':
            self._hits = self._completion_list[:]
            self.position = event.widget.index(tk.INSERT)
        if event.keysym in ('Left', 'Right', 'Shift_R', 'Shift_L', 'Control_R', 'Control_L', 'Alt_R', 'Alt_L'):
            return
        if event.keysym in ('Shift_R', 'Shift_L', 'Control_R', 'Control_L', 'Alt_R', 'Alt_L'):
            return
        if event.keysym == 'Return':
            return
        if event.keysym == 'Tab':
            self._hits = self._completion_list[:]
            self.position = event.widget.index(tk.INSERT)
            self.autocomplete(1)
            return
        if event.keysym == 'Shift_R':
            return
        if event.keysym == 'Shift_L':
            return
        if event.keysym == 'Control_R':
            return
        if event.keysym == 'Control_L':
            return
        if event.keysym == 'Alt_R':
            return
        if event.keysym == 'Alt_L':
            return
        if event.keysym in ('Up', 'Down', 'Shift_R', 'Shift_L', 'Control_R', 'Control_L', 'Alt_R', 'Alt_L'):
            return
        if event.keysym in ('Left', 'Right', 'Shift_R', 'Shift_L', 'Control_R', 'Control_L', 'Alt_R', 'Alt_L'):
            return
        if event.keysym == 'BackSpace':
            self._hits = self._completion_list[:]
            self.position = event.widget.index(tk.INSERT) - 1
            if self.position < 0:
                self.position = 0
            if self._hits != self._hits:
                self._hit_index = 0
                self._hits = self._hits
            self.update()
        if event.keysym in ('Return', 'KP_Enter'):
            self._hits = self._completion_list[:]
            self.update()
            self.position = event.widget.index(tk.INSERT)
            return
        if event.keysym in ('Up', 'Down', 'Shift_R', 'Shift_L', 'Control_R', 'Control_L', 'Alt_R', 'Alt_L'):
            return
        if event.keysym in ('Left', 'Right', 'Shift_R', 'Shift_L', 'Control_R', 'Control_L', 'Alt_R', 'Alt_L'):
            return
        if event.keysym == 'BackSpace':
            self._hits = self._completion_list[:]
            self.position = event.widget.index(tk.INSERT) - 1
            if self.position < 0:
                self.position = 0
            if self._hits != self._hits:
                self._hit_index = 0
                self._hits = self._hits
            self.update()
        if event.keysym in ('Return', 'KP_Enter'):
            self._hits = self._completion_list[:]
            self.update()
            self.position = event.widget.index(tk.INSERT)
            return
        if event.keysym == 'Tab':
            self._hits = self._completion_list[:]
            self.position = event.widget.index(tk.INSERT)
            self.autocomplete(1)
            return
        if event.keysym == 'Shift_R':
            return
        if event.keysym == 'Shift_L':
            return
        if event.keysym == 'Control_R':
            return
        if event.keysym == 'Control_L':
            return
        if event.keysym == 'Alt_R':
            return
        if event.keysym == 'Alt_L':
            return
        self._hits = self._completion_list[:]
        if event.keysym == 'Return':
            return
        if event.keysym == 'Tab':
            return
        if event.keysym == 'Shift_R':
            return
        if event.keysym == 'Shift_L':
            return
        if event.keysym == 'Control_R':
            return
        if event.keysym == 'Control_L':
            return
        if event.keysym == 'Alt_R':
            return
        if event.keysym == 'Alt_L':
            return
        if len(event.keysym) == 1:
            self.autocomplete()
            if self.show_popup == False:
                self.show_popup = True
                self.autocomplete(0)
            else:
                self.autocomplete()
        else:
            if self.show_popup == True:
                self.show_popup = False
                self.autocomplete(0)

# Define the create_file_dialog function
def create_file_dialog():
    global filename  # Define filename as a global variable
    filename = simpledialog.askstring("Create File", "Enter the name of the new file:")
    if filename:
        create_file_gui(filename)

# Create the main application window
app = tk.Tk()
app.title("GitHub GUI")

# Create and configure widgets
username_label = tk.Label(app, text="Enter your GitHub username:")
username_label.pack()
username_entry = tk.Entry(app)
username_entry.pack()

token_label = tk.Label(app, text="Enter your personal access token:")
token_label.pack()
token_entry = tk.Entry(app)
token_entry.pack()

search_label = tk.Label(app, text="Search for a repository:")
search_label.pack()

search_var = tk.StringVar()
search_var.trace_add("write", on_search_entry_change)
search_entry = tk.Entry(app, textvariable=search_var)
search_entry.pack()

search_button = tk.Button(app, text="Search", command=fetch_repos)
search_button.pack()

repo_label = tk.Label(app, text="Select a repository:")
repo_label.pack()

repo_combobox = AutocompleteCombobox(app, values=[], state="readonly")
repo_combobox.pack()

browse_button = tk.Button(app, text="Browse Repository", command=browse_repository)
browse_button.pack()

# Create a Treeview widget for file and folder navigation
file_tree = ttk.Treeview(app)
file_tree.pack()

create_button = tk.Button(app, text="Create File", command=create_file_dialog)
create_button.pack()

app.mainloop()
