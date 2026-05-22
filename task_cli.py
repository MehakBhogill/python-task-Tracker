#!/usr/bin/env python3
import json  #to use json file
import os    #to check file esistence
import sys 
import argparse  # to run CLI commands
from datetime import datetime  # for using date
from pathlib import Path  # modern way to handle file path

class TaskCLI:    # object of this class will manage all tasks
    def __init__(self, filename="tasks.json"):   # constructor
        self.filename = filename
        self.tasks = []
        self.load_tasks()
    
    def load_tasks(self):
        """Load tasks from JSON file"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    self.tasks = json.load(f)
                    # Fix any tasks missing fields
                    for task in self.tasks:
                        if 'updated_at' not in task:
                            task['updated_at'] = task.get('created_at', datetime.now().isoformat())
                        if 'created_at' not in task:
                            task['created_at'] = datetime.now().isoformat()
                        if 'status' not in task:
                            task['status'] = 'todo'
            except json.JSONDecodeError:
                self.tasks = []
        else:
            self.tasks = []
    
    def save_tasks(self):
        """Save tasks to JSON file"""
        with open(self.filename, 'w') as f:
            json.dump(self.tasks, f, indent=2)
    
    def get_next_id(self):
        """Get the next available task ID"""
        if not self.tasks:
            return 1
        return max(task['id'] for task in self.tasks) + 1
    
    def add_task(self, description):
        """Add a new task"""
        now = datetime.now().isoformat()
        task = {
            'id': self.get_next_id(),
            'description': description,
            'status': 'todo',
            'created_at': now,
            'updated_at': now
        }
        self.tasks.append(task)
        self.save_tasks()
        print(f"Task added successfully (ID: {task['id']})")
    
    def update_task(self, task_id, description):
        """Update a task's description"""
        task = self.find_task(task_id)
        if task:
            task['description'] = description
            task['updated_at'] = datetime.now().isoformat()
            self.save_tasks()
            print(f"Task {task_id} updated successfully")
        else:
            print(f"Error: Task with ID {task_id} not found")
    
    def delete_task(self, task_id):
        """Delete a task"""
        task = self.find_task(task_id)
        if task:
            self.tasks = [t for t in self.tasks if t['id'] != task_id]
            self.save_tasks()
            print(f"Task {task_id} deleted successfully")
        else:
            print(f"Error: Task with ID {task_id} not found")
    
    def mark_task(self, task_id, status):
        """Mark a task with a specific status"""
        valid_statuses = ['todo', 'in-progress', 'done']
        if status not in valid_statuses:
            print(f"Error: Invalid status. Use: {', '.join(valid_statuses)}")
            return
        
        task = self.find_task(task_id)
        if task:
            task['status'] = status
            task['updated_at'] = datetime.now().isoformat()
            self.save_tasks()
            print(f"Task {task_id} marked as {status}")
        else:
            print(f"Error: Task with ID {task_id} not found")
    
    def find_task(self, task_id):
        """Find a task by ID"""
        for task in self.tasks:
            if task['id'] == task_id:
                return task
        return None
    
    def list_tasks(self, status=None):
        """List tasks, optionally filtered by status"""
        if status:
            filtered_tasks = [t for t in self.tasks if t['status'] == status]
            status_names = {
                'todo': 'todo',
                'in-progress': 'in progress',
                'done': 'done'
            }
            print(f"\nTasks ({status_names.get(status, status)}):")
        else:
            filtered_tasks = self.tasks
            print("\nAll tasks:")
        
        if not filtered_tasks:
            print("  No tasks found")
            return
        
        for task in filtered_tasks:
            status_display = {
                'todo': '📝',
                'in-progress': '🔄',
                'done': '✅'
            }.get(task['status'], '•')
            
            print(f"  [{task['id']}] {status_display} {task['description']}")
            print(f"       Status: {task['status']}")
            # Safely handle missing or malformed timestamps
            updated_at = task.get('updated_at', task.get('created_at', 'Unknown'))
            if updated_at != 'Unknown' and isinstance(updated_at, str):
                updated_at = updated_at[:19]  # Truncate microseconds
            print(f"       Updated: {updated_at}")
            print()

def main():
    parser = argparse.ArgumentParser(
        description='Task CLI - A command line task manager',
        usage='task-cli <command> [arguments]'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Add command
    parser_add = subparsers.add_parser('add', help='Add a new task')
    parser_add.add_argument('description', help='Task description')
    
    # Update command
    parser_update = subparsers.add_parser('update', help='Update a task')
    parser_update.add_argument('id', type=int, help='Task ID')
    parser_update.add_argument('description', help='New task description')
    
    # Delete command
    parser_delete = subparsers.add_parser('delete', help='Delete a task')
    parser_delete.add_argument('id', type=int, help='Task ID')
    
    # Mark commands
    parser_mark_progress = subparsers.add_parser('mark-in-progress', help='Mark task as in progress')
    parser_mark_progress.add_argument('id', type=int, help='Task ID')
    
    parser_mark_done = subparsers.add_parser('mark-done', help='Mark task as done')
    parser_mark_done.add_argument('id', type=int, help='Task ID')
    
    # List command
    parser_list = subparsers.add_parser('list', help='List tasks')
    parser_list.add_argument('status', nargs='?', choices=['todo', 'in-progress', 'done'], 
                            help='Filter tasks by status')
    
    args = parser.parse_args()
    
    cli = TaskCLI()
    
    if args.command == 'add':
        cli.add_task(args.description)
    elif args.command == 'update':
        cli.update_task(args.id, args.description)
    elif args.command == 'delete':
        cli.delete_task(args.id)
    elif args.command == 'mark-in-progress':
        cli.mark_task(args.id, 'in-progress')
    elif args.command == 'mark-done':
        cli.mark_task(args.id, 'done')
    elif args.command == 'list':
        cli.list_tasks(args.status)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
