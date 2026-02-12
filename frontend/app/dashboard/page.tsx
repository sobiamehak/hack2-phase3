'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import TodoForm from '../../components/TodoForm';
import TodoList from '../../components/TodoList';
import ProtectedRoute from '../../components/ProtectedRoute';

interface Task {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  created_at: string;
}

export default function Dashboard() {
  const { user, logout, loading: authLoading } = useAuth();
  const router = useRouter();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');

  // Check if user is authenticated (wait for auth to finish loading first)
  useEffect(() => {
    if (authLoading) return;
    if (!user) {
      router.push('/login');
    } else {
      fetchTasks();
    }
  }, [user, router, authLoading]);

  // Refresh tasks when chatbot modifies them
  useEffect(() => {
    const handler = () => fetchTasks();
    window.addEventListener('tasks-updated', handler);
    return () => window.removeEventListener('tasks-updated', handler);
  }, [user]);

  const fetchTasks = async () => {
    if (!user) return;
    try {
      setLoading(true);
      // Fetch tasks from the API
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}/api/${user.id}/tasks/`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`Failed to fetch tasks: ${response.status} ${response.statusText}`);
      }
      
      const tasksData = await response.json();
      setTasks(tasksData);
    } catch (err) {
      setError('Failed to load tasks');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddTask = async (title: string, description: string) => {
    if (!user) return;
    try {
      const backendUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
      const response = await fetch(`${backendUrl}/api/${user.id}/tasks/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ title, description: description || null }),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || 'Failed to add task');
      }

      setError('');
      await fetchTasks();
    } catch (err: any) {
      setError(err.message || 'Failed to add task');
      console.error(err);
    }
  };

  const toggleTaskCompletion = async (taskId: string) => {
    if (!user) return;
    try {
      const backendUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
      const response = await fetch(`${backendUrl}/api/${user.id}/tasks/${taskId}/complete`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to update task');
      }

      await fetchTasks();
    } catch (err: any) {
      setError(err.message || 'Failed to update task');
      console.error(err);
    }
  };

  const deleteTask = async (taskId: string) => {
    if (!user) return;
    try {
      const backendUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
      const response = await fetch(`${backendUrl}/api/${user.id}/tasks/${taskId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to delete task');
      }

      await fetchTasks();
    } catch (err: any) {
      setError(err.message || 'Failed to delete task');
      console.error(err);
    }
  };

  if (authLoading || !user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-xl text-gray-600 flex items-center">
          <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Loading your tasks...
        </div>
      </div>
    );
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        {/* Header */}
        <header className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-5">
              <Link href="/" className="flex items-center">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                  </svg>
                </div>
                <span className="ml-3 text-xl font-bold text-gray-900">TodoApp</span>
              </Link>

              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                    <span className="text-blue-800 font-medium text-sm">
                      {user.name ? user.name.charAt(0).toUpperCase() : user.email ? user.email.charAt(0).toUpperCase() : 'U'}
                    </span>
                  </div>
                  <span className="text-gray-700 font-medium hidden sm:block">
                    {user.email || user.name || 'User'}
                  </span>
                </div>

                <button
                  onClick={logout}
                  className="btn-danger flex items-center"
                >
                  <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
                  </svg>
                  Logout
                </button>
              </div>
            </div>
          </div>
        </header>

        <main className="max-w-5xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-10">
            <h1 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
              Your Task Dashboard
            </h1>
            <p className="mt-3 max-w-2xl mx-auto text-xl text-gray-500">
              Organize your work and life, one task at a time.
            </p>
          </div>

          {error && (
            <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-6">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-red-700">
                    {error}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Stats Overview */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="card text-center">
              <div className="text-3xl font-bold text-blue-600">{tasks.length}</div>
              <div className="text-gray-600">Total Tasks</div>
            </div>
            <div className="card text-center">
              <div className="text-3xl font-bold text-green-600">{tasks.filter(t => t.completed).length}</div>
              <div className="text-gray-600">Completed</div>
            </div>
            <div className="card text-center">
              <div className="text-3xl font-bold text-yellow-600">{tasks.filter(t => !t.completed).length}</div>
              <div className="text-gray-600">Pending</div>
            </div>
          </div>

          {/* Create Task Form */}
          <div className="card mb-8">
            <h2 className="text-xl font-bold text-gray-900 mb-6">Create New Task</h2>
            <TodoForm onAddTask={handleAddTask} />
          </div>

          {/* Tasks List */}
          <div className="card">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-gray-900">Your Tasks</h2>
              <span className="text-sm text-gray-500">{tasks.length} tasks</span>
            </div>

            <div className="border-t border-gray-200 pt-6">
              <TodoList
                todos={tasks}
                onToggle={toggleTaskCompletion}
                onDelete={deleteTask}
              />
            </div>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}