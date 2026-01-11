import React, { useState, useEffect } from 'react';
import { GripVertical, Plus, X, RefreshCw, LogIn } from 'lucide-react';
import api from './api';
import './kanbanbord.css';

const KANBAN_STORAGE_KEY = 'kanban_board_data';

// Helper functions for localStorage
const saveToLocalStorage = (data) => {
  try {
    localStorage.setItem(KANBAN_STORAGE_KEY, JSON.stringify(data));
  } catch (error) {
    console.error('Error saving to localStorage:', error);
  }
};

const loadFromLocalStorage = () => {
  try {
    const data = localStorage.getItem(KANBAN_STORAGE_KEY);
    return data ? JSON.parse(data) : null;
  } catch (error) {
    console.error('Error loading from localStorage:', error);
    return null;
  }
};

const KanbanBoard = ({ isAuthenticated: propIsAuthenticated }) => {
  const [columns, setColumns] = useState({
    todo: {
      title: 'To Do',
      items: []
    },
    inProgress: {
      title: 'In Progress',
      items: []
    },
    done: {
      title: 'Done',
      items: []
    }
  });

  const [draggedItem, setDraggedItem] = useState(null);
  const [draggedFrom, setDraggedFrom] = useState(null);
  const [newTaskInput, setNewTaskInput] = useState('');
  const [showInput, setShowInput] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(propIsAuthenticated ?? false);

  // Save to localStorage whenever columns change
  useEffect(() => {
    if (!loading && isAuthenticated) {
      saveToLocalStorage(columns);
    }
  }, [columns, loading, isAuthenticated]);

  // Sync auth state from props
  useEffect(() => {
    if (propIsAuthenticated !== undefined) {
      setIsAuthenticated(propIsAuthenticated);
      if (propIsAuthenticated) {
        loadData();
      } else {
        // Clear data when logged out
        setColumns({
          todo: { title: 'To Do', items: [] },
          inProgress: { title: 'In Progress', items: [] },
          done: { title: 'Done', items: [] }
        });
        setLoading(false);
      }
    } else {
      // Fallback: check auth status if no prop provided
      checkAuthStatus();
    }
  }, [propIsAuthenticated]);

  // Auto-sync every 5 minutes
  useEffect(() => {
    if (!isAuthenticated) return;

    const interval = setInterval(() => {
      console.log('Auto-syncing Kanban data...');
      fetchFromAPI();
    }, 5 * 60 * 1000); // 5 minutes

    return () => clearInterval(interval);
  }, [isAuthenticated]);

  // Listen for custom events when tasks/events are added from other components
  useEffect(() => {
    const handleTaskAdded = () => {
      console.log('Task added event received, syncing...');
      fetchFromAPI();
    };

    const handleEventAdded = () => {
      console.log('Calendar event added, syncing...');
      fetchFromAPI();
    };

    window.addEventListener('kanban-task-added', handleTaskAdded);
    window.addEventListener('kanban-event-added', handleEventAdded);

    return () => {
      window.removeEventListener('kanban-task-added', handleTaskAdded);
      window.removeEventListener('kanban-event-added', handleEventAdded);
    };
  }, []);

  const checkAuthStatus = async () => {
    setLoading(true);
    try {
      const response = await api.get('/auth/status', { withCredentials: true });
      console.log('Kanban Auth status:', response.data);
      if (response.data?.authenticated) {
        setIsAuthenticated(true);
        await loadData();
      } else {
        setIsAuthenticated(false);
        setLoading(false);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      setIsAuthenticated(false);
      setLoading(false);
    }
  };

  const loadData = async () => {
    setLoading(true);

    // First, try to load from localStorage
    const savedData = loadFromLocalStorage();

    if (savedData && savedData.todo && savedData.inProgress && savedData.done) {
      // Use saved data if it exists
      setColumns(savedData);
      setLoading(false);
    } else {
      // Otherwise fetch from API
      await fetchFromAPI();
    }
  };

  const fetchFromAPI = async () => {
    try {
      setLoading(true);
      const [eventsRes, tasksRes] = await Promise.all([
        api.get('/calendar/events', { withCredentials: true }),
        api.get('/tasks/', { withCredentials: true })
      ]);

      const calendarItems = (eventsRes.data || []).map(event => ({
        id: `cal-${event.id}`,
        content: `📅 ${event.summary}`,
        type: 'calendar',
        originalId: event.id
      }));

      const rawTasks = tasksRes.data?.tasks ?? tasksRes.data ?? [];
      const tasks = Array.isArray(rawTasks) ? rawTasks : [];

      const todoTasks = tasks.filter(t => t.status !== 'completed').map(task => ({
        id: `task-${task.id}`,
        content: `✅ ${task.title}`,
        type: 'task',
        originalId: task.id
      }));

      const doneTasks = tasks.filter(t => t.status === 'completed').map(task => ({
        id: `task-${task.id}`,
        content: `✅ ${task.title}`,
        type: 'task',
        originalId: task.id
      }));

      const newColumns = {
        todo: {
          title: 'To Do',
          items: [...calendarItems, ...todoTasks]
        },
        inProgress: {
          title: 'In Progress',
          items: []
        },
        done: {
          title: 'Done',
          items: doneTasks
        }
      };

      setColumns(newColumns);
    } catch (error) {
      console.error("Error fetching Kanban data:", error);
      if (error.response && error.response.status === 401) {
        setIsAuthenticated(false);
      }
    } finally {
      setLoading(false);
    }
  };

  // Sync/refresh data from API (manual refresh button)
  const handleRefresh = async () => {
    await fetchFromAPI();
  };

  const onDragStart = (e, item, columnId) => {
    setDraggedItem(item);
    setDraggedFrom(columnId);
    e.dataTransfer.effectAllowed = 'move';
  };

  const onDragOver = (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  const onDrop = async (e, columnId) => {
    e.preventDefault();

    if (!draggedItem || !draggedFrom) return;

    if (draggedFrom === columnId) {
      setDraggedItem(null);
      setDraggedFrom(null);
      return;
    }

    // Sync with backend if moving to 'done'
    if (columnId === 'done' && draggedItem.type === 'task') {
      try {
        await api.put(`/tasks/${draggedItem.originalId}/complete`);
      } catch (error) {
        console.error("Error completing task:", error);
      }
    }

    const newColumns = { ...columns };

    newColumns[draggedFrom].items = newColumns[draggedFrom].items.filter(
      item => item.id !== draggedItem.id
    );

    newColumns[columnId].items = [...newColumns[columnId].items, draggedItem];

    setColumns(newColumns);
    setDraggedItem(null);
    setDraggedFrom(null);
  };

  const addTask = async (columnId) => {
    if (!newTaskInput.trim()) return;

    // Create local task first for immediate feedback
    const localTask = {
      id: `local-${Date.now()}`,
      content: `✅ ${newTaskInput}`,
      type: 'local',
      originalId: null
    };

    // Add to state immediately
    const updatedColumns = {
      ...columns,
      [columnId]: {
        ...columns[columnId],
        items: [...columns[columnId].items, localTask]
      }
    };
    setColumns(updatedColumns);
    setNewTaskInput('');
    setShowInput(null);

    // Try to sync with backend
    try {
      const response = await api.post('/tasks/', {
        title: newTaskInput,
        notes: "Added via Kanban Board"
      });

      // Update the local task with the real ID from backend
      const newTask = {
        id: `task-${response.data.id}`,
        content: `✅ ${response.data.title}`,
        type: 'task',
        originalId: response.data.id
      };

      setColumns(prev => ({
        ...prev,
        [columnId]: {
          ...prev[columnId],
          items: prev[columnId].items.map(item =>
            item.id === localTask.id ? newTask : item
          )
        }
      }));
    } catch (error) {
      console.error("Error adding task to backend:", error);
      // Task remains local - that's okay, it will be saved to localStorage
    }
  };

  const deleteItem = async (columnId, item) => {
    // Remove from state immediately
    setColumns({
      ...columns,
      [columnId]: {
        ...columns[columnId],
        items: columns[columnId].items.filter(i => i.id !== item.id)
      }
    });

    // Try to sync with backend
    try {
      if (item.type === 'task' && item.originalId) {
        await api.delete(`/tasks/${item.originalId}`);
      }
      // Calendar event deletion not implemented in backend router yet
    } catch (error) {
      console.error("Error deleting item from backend:", error);
      // Item already removed from local state, that's fine
    }
  };

  const handleLogin = () => {
    window.location.href = 'http://localhost:8000/auth/login';
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <div>Loading Kanban data...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="kanban-board-container">
        <div className="login-prompt">
          <LogIn size={48} className="login-icon" />
          <h2>Please Login</h2>
          <p>You need to be logged in to view and manage your tasks and calendar events.</p>
          <button onClick={handleLogin} className="login-btn-kanban">
            Login with Google
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="kanban-board-container">
      <div className="kanban-header">
        <h1 className="kanban-title">Work Management Board</h1>
        <button onClick={handleRefresh} className="refresh-btn" title="Sync with Google">
          <RefreshCw size={18} />
          <span>Sync</span>
        </button>
      </div>

      <div className="kanban-columns-wrapper">
        {Object.entries(columns).map(([columnId, column]) => (
          <div
            key={columnId}
            className="kanban-column"
            onDragOver={onDragOver}
            onDrop={(e) => onDrop(e, columnId)}
          >
            <div className="kanban-column-header">
              <h2>
                {column.title}
                <span className="kanban-count">{column.items.length}</span>
              </h2>
              <button
                onClick={() => setShowInput(columnId)}
                className="add-task-btn"
                title="Add task"
              >
                <Plus size={20} />
              </button>
            </div>

            <div className="kanban-items-list">
              {showInput === columnId && (
                <div className="kanban-input-area">
                  <input
                    type="text"
                    value={newTaskInput}
                    onChange={(e) => setNewTaskInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && addTask(columnId)}
                    placeholder="New task title..."
                    className="kanban-input"
                    autoFocus
                  />
                  <div className="kanban-input-actions">
                    <button onClick={() => addTask(columnId)} className="btn-primary">Add</button>
                    <button onClick={() => { setShowInput(null); setNewTaskInput(''); }} className="btn-secondary">Cancel</button>
                  </div>
                </div>
              )}
              {column.items.map((item) => (
                <div
                  key={item.id}
                  draggable
                  onDragStart={(e) => onDragStart(e, item, columnId)}
                  className="kanban-item"
                >
                  <p>{item.content}</p>
                  <div className="item-footer">
                    <GripVertical size={14} className="grip-icon" />
                    <button
                      onClick={() => deleteItem(columnId, item)}
                      className="delete-item-btn"
                      title="Delete item"
                    >
                      <X size={14} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default KanbanBoard;