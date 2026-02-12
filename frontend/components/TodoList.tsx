'use client';

import TodoItem from './TodoItem';

interface Todo {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  created_at: string;
}

interface TodoListProps {
  todos: Todo[];
  onToggle: (id: string) => void;
  onDelete: (id: string) => void;
}

export default function TodoList({ todos, onToggle, onDelete }: TodoListProps) {
  if (todos.length === 0) {
    return (
      <div className="px-4 py-5 sm:p-6 text-center text-gray-500">
        No tasks yet. Create your first task above!
      </div>
    );
  }

  return (
    <ul className="divide-y divide-gray-200">
      {todos.map((todo) => (
        <TodoItem
          key={todo.id}
          todo={todo}
          onToggle={onToggle}
          onDelete={onDelete}
        />
      ))}
    </ul>
  );
}