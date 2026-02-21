import React, { useState, useEffect } from 'react';

const API_BASE = 'http://localhost:8000/api';

// ── Simple API helper ────────────────────────────────────────────────────────
const api = {
  token: localStorage.getItem('token') || '',

  async request(method, path, body = null) {
    const res = await fetch(`${API_BASE}${path}`, {
      method,
      headers: {
        'Content-Type': 'application/json',
        ...(this.token ? { Authorization: `Bearer ${this.token}` } : {}),
      },
      body: body ? JSON.stringify(body) : null,
    });
    return res.json();
  },

  get: (path) => api.request('GET', path),
  post: (path, body) => api.request('POST', path, body),
  patch: (path, body) => api.request('PATCH', path, body),
  delete: (path) => api.request('DELETE', path),
};

// ── Status column colors ─────────────────────────────────────────────────────
const STATUS_COLORS = {
  todo: '#ef4444',
  in_progress: '#f59e0b',
  done: '#22c55e',
};

// ── Main App ─────────────────────────────────────────────────────────────────
export default function App() {
  const [token, setToken] = useState(localStorage.getItem('token') || '');
  const [tasks, setTasks] = useState([]);
  const [newTask, setNewTask] = useState({ title: '', description: '' });
  const [loginData, setLoginData] = useState({ username: '', password: '' });
  const [message, setMessage] = useState('');

  // Load tasks on login
  useEffect(() => {
    if (token) {
      api.token = token;
      loadTasks();
      // Setup WebSocket for real-time updates (connects to all tasks)
    }
  }, [token]);

  const loadTasks = async () => {
    const data = await api.get('/tasks/');
    setTasks(data.results || data);
  };

  const login = async () => {
    const data = await fetch(`${API_BASE}/token/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(loginData),
    }).then(r => r.json());

    if (data.access) {
      localStorage.setItem('token', data.access);
      api.token = data.access;
      setToken(data.access);
    } else {
      setMessage('Login failed. Check your credentials.');
    }
  };

  const createTask = async () => {
    if (!newTask.title) return;
    await api.post('/tasks/', { ...newTask, status: 'todo' });
    setNewTask({ title: '', description: '' });
    loadTasks();
  };

  const updateStatus = async (task, newStatus) => {
    await api.patch(`/tasks/${task.id}/`, { status: newStatus });
    loadTasks();
  };

  const deleteTask = async (id) => {
    await api.delete(`/tasks/${id}/`);
    loadTasks();
  };

  // ── Login screen ───────────────────────────────────────────────────────────
  if (!token) {
    return (
      <div style={styles.center}>
        <div style={styles.card}>
          <h2 style={styles.title}>🤖 AI Platform Login</h2>
          <input
            style={styles.input}
            placeholder="Username"
            value={loginData.username}
            onChange={e => setLoginData({ ...loginData, username: e.target.value })}
          />
          <input
            style={styles.input}
            type="password"
            placeholder="Password"
            value={loginData.password}
            onChange={e => setLoginData({ ...loginData, password: e.target.value })}
          />
          <button style={styles.btn} onClick={login}>Login</button>
          {message && <p style={{ color: 'red' }}>{message}</p>}
        </div>
      </div>
    );
  }

  // ── Board view ─────────────────────────────────────────────────────────────
  const columns = ['todo', 'in_progress', 'done'];

  return (
    <div style={styles.app}>
      <div style={styles.header}>
        <h1 style={styles.title}>🤖 AI Task Platform</h1>
        <button style={{ ...styles.btn, background: '#6b7280' }}
          onClick={() => { localStorage.removeItem('token'); setToken(''); }}>
          Logout
        </button>
      </div>

      {/* Create Task */}
      <div style={styles.createBox}>
        <input
          style={{ ...styles.input, width: '200px' }}
          placeholder="Task title"
          value={newTask.title}
          onChange={e => setNewTask({ ...newTask, title: e.target.value })}
        />
        <input
          style={{ ...styles.input, width: '300px' }}
          placeholder="Description (optional)"
          value={newTask.description}
          onChange={e => setNewTask({ ...newTask, description: e.target.value })}
        />
        <button style={styles.btn} onClick={createTask}>+ Add Task</button>
      </div>

      {/* Kanban Board */}
      <div style={styles.board}>
        {columns.map(col => (
          <div key={col} style={styles.column}>
            <div style={{ ...styles.colHeader, background: STATUS_COLORS[col] }}>
              {col.replace('_', ' ').toUpperCase()} ({tasks.filter(t => t.status === col).length})
            </div>
            {tasks.filter(t => t.status === col).map(task => (
              <div key={task.id} style={styles.taskCard}>
                <strong>{task.title}</strong>
                <p style={{ fontSize: '13px', color: '#6b7280' }}>{task.description}</p>
                <div style={styles.taskActions}>
                  {columns.filter(c => c !== col).map(c => (
                    <button key={c} style={{ ...styles.smallBtn, background: STATUS_COLORS[c] }}
                      onClick={() => updateStatus(task, c)}>
                      → {c.replace('_', ' ')}
                    </button>
                  ))}
                  <button style={{ ...styles.smallBtn, background: '#ef4444' }}
                    onClick={() => deleteTask(task.id)}>🗑</button>
                </div>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Styles ────────────────────────────────────────────────────────────────────
const styles = {
  app: { fontFamily: 'sans-serif', padding: '20px', background: '#f3f4f6', minHeight: '100vh' },
  center: { display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', background: '#f3f4f6' },
  card: { background: 'white', padding: '40px', borderRadius: '12px', boxShadow: '0 4px 20px rgba(0,0,0,0.1)', width: '320px' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' },
  title: { margin: 0, color: '#1f2937' },
  input: { display: 'block', width: '100%', padding: '10px', margin: '8px 0', border: '1px solid #d1d5db', borderRadius: '6px', boxSizing: 'border-box' },
  btn: { padding: '10px 20px', background: '#3b82f6', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', marginLeft: '8px' },
  createBox: { display: 'flex', alignItems: 'center', background: 'white', padding: '16px', borderRadius: '8px', marginBottom: '20px', boxShadow: '0 1px 4px rgba(0,0,0,0.08)' },
  board: { display: 'flex', gap: '16px' },
  column: { flex: 1, background: 'white', borderRadius: '8px', overflow: 'hidden', boxShadow: '0 1px 4px rgba(0,0,0,0.08)' },
  colHeader: { padding: '12px 16px', color: 'white', fontWeight: 'bold', fontSize: '14px' },
  taskCard: { padding: '12px 16px', borderBottom: '1px solid #f3f4f6' },
  taskActions: { display: 'flex', gap: '6px', marginTop: '8px', flexWrap: 'wrap' },
  smallBtn: { padding: '4px 8px', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' },
};
