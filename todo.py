import json, sqlite3
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
def add_task(task_name):
    due_date = input("Enter due date (YYYY-MM-DD) or leave blank: ")
    priority= input("Enter priority (1-5, default 3): ") or "3"
    try:
        priority = int(priority)
        if not (1<=priority<=5):
            raise ValueError
    except ValueError:
        print(Fore.RED + "Invalid priority. Defaulting to 3.")
        priority = 3

    with sqlite3.connect(DB_FILE) as conn:
        cursor= conn.cursor()
        cursor.execute("INSERT INTO tasks (task, due_date, priority) VALUES (?,?,?)", (task_name,due_date,priority))
        conn.commit()
        
    print(f"✅ Task added: {task_name} | Due: {due_date or 'No Due Date'} | Priority: {priority}")


def list_tasks():
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory =sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, task, completed, due_date, priority FROM tasks ORDER BY priority DESC")
        tasks = cursor.fetchall()

    if not tasks:
        print(Fore.YELLOW + "📭 No tasks found.")
        return
    
    print("\n 📋 Your To-Do List: \n ")
    for task in tasks:
        status= Fore.GREEN + "✅" if task["completed"] else Fore.RED + "❌"
        due_info = f"🗓️ {task['due_date']}" if task["due_date"] else ""
        print(f"{task['id']}. {status} {task['task']} {due_info}  🔥 Priority: {task['priority']}")

#Mark Completed:
def mark_completed():
    list_tasks()
    try:
        task_no= int(input(Fore.GREEN + "Enter the task number to mark as completed: "))
    except ValueError:
        print(Fore.RED + "Invalid task number.")
        return

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_no,))
        if cursor.rowcount == 0:
            print(Fore.RED + "Task not found.")
            return
        else:
            conn.commit()
            print(f"🎉 Task {task_no} marked as completed.")

#Delete tasks:
def delete_task():
    list_tasks()
    try:
        task_no= int(input(Fore.RED + "Enter the task number to delete: "))
    except ValueError:
        print(Fore.RED + "Invalid task number.")
        return
    
    with sqlite3.connect(DB_FILE) as conn:
        cursor= conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?",(task_no,))
        if cursor.rowcount == 0:
            print(Fore.RED + "Task not found.")
        else:
            conn.commit()
            print(f"🗑️ Task {task_no} deleted.")


#Main Program

if __name__ == "__main__":
    connect_db()

    while True:
        print(Fore.YELLOW + "\n 📌 To-Do List Menu")
        print(Fore.BLUE + "1. Add Task")
        print(Fore.BLUE + "2. List Tasks")
        print(Fore.BLUE + "3. Mark Task as Completed")
        print(Fore.BLUE + "4. Delete Task")
        print(Fore.RED + "5. Exit")

        choice = input(Fore.YELLOW + "Enter an option:")

        if choice == "1":
            task = input(Fore.GREEN + "Enter a new Task:")
            add_task(task)

        elif choice =="2":
            list_tasks()
        elif choice == "3":
            list_tasks()
            task_no = int(input(Fore.GREEN + "Enter the task number to mark as completed:")) 
            mark_completed()
        elif choice == "4":
            list_tasks()
            task_no= int(input(Fore.RED + "Enter the task number to delete:"))

            delete_task()

        elif choice == "5":
            print(Fore.MAGENTA + "👋Goodbye!")
            break
        else:
            print(Fore.RED + "Invalid choice. Please try again.")



