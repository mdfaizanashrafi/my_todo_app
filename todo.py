import json, sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from colorama import Fore, Style, init

init(autoreset=True)
#create a db file
DB_FILE = "tasks.db"

def connect_db():
    conn= sqlite3.connect(DB_FILE)
    cursor= conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            due_date TEXT,
            priority INTEGER DEFAULT 3
        )
    """)

    conn.commit()
    conn.close()
  

TASKS_FILE = "tasks.json"

#Load existing task from a file
def load_tasks():
    try: 
        with open(TASKS_FILE,'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    
#Save task to a file
def save_tasks(tasks):
    with open(TASKS_FILE,'w') as file:
        json.dump(tasks, file, indent=4)

#Add new tasks
def add_task():
    task_name= task_entry.get()
    due_date= due_date_entry.get()
    priority= priority_var.get() or "3"

    if not task_name:
        messagebox.showerror("Error","Task cannot be empty!")
        return
    
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (task, due_date, priority) VALUES (?, ?, ?)", (task_name, due_date, priority))
        conn.commit()
    
    task_entry.delete(0,tk.END)
    due_date_entry.delete(0,tk.END)
    list_tasks()

def list_tasks():
    tasks_list.delete(0,tk.END)  #clears the listbox first
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory =sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, task, completed, due_date, priority FROM tasks ORDER BY priority DESC")
        tasks = cursor.fetchall()

    for task in tasks:
        status="✅" if task[2] else "❌"
        due_info = f"🗓️ {task[3]}" if task[3] else ""
        tasks_list.insert(tk.END, f"{task[0]}. {status} {task[1]} {due_info} 🔥 Priority: {task[4]}")

#Mark Completed:
def mark_completed():
    selected_task=tasks_list.curselection()
    if not selected_task:
        messagebox.showerror("Error","Select a task first!")
    
    task_id = tasks_list.get(selected_task).split(".")[0]
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
        conn.commit()

    list_tasks()

#Delete tasks:
def delete_task():
    selected_task=tasks_list.curselection()
    if not selected_task:
        messagebox.showerror("Error","Select a task first!")
        return
    
    task_id = tasks_list.get(selected_task).split(".")[0]
    with sqlite3.connect(DB_FILE) as conn:
        cursor= conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?",(task_id,))
        conn.commit()
        
    list_tasks()


#Main Program

root= tk.Tk()
root.title("📝 To-Do List App")

#tasak input fields
task_entry= tk.Entry(root,width=40)
task_entry.pack(pady=5)

due_date_entry=tk.Entry(root,width=20)
due_date_entry.pack(pady=5)

priority_var= tk.Entry(root,width=10)
priority_var.pack(pady=5)

#task listbox
tasks_list=tk.Listbox(root,width=60,height= 10, font=("Arial", 12))
tasks_list.pack(pady=5)

#buttons:
tk.Button(root,text="➕ Add Task",command=add_task).pack(pady=2)
tk.Button(root,text="✅ Mark Completed",command=mark_completed).pack(pady=2)
tk.Button(root,text="🗑️ Delete Task",command=delete_task).pack(pady=2)

list_tasks()
root.mainloop() #starts the GUI loop


