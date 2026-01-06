import './App.css';
import Calendar from './Calendar.jsx';
import React, { useState, useEffect, useCallback } from 'react';
import api from './api';
const App = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userEmail, setUserEmail] = useState('');
  const [userName, setusername] = useState('');
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);
  const [authError, setAuthError] = useState('');
  const [upcomingEvents, setUpcomingEvents] = useState([]);
  const [eventsError, setEventsError] = useState('');
  const [isLoadingEvents, setIsLoadingEvents] = useState(false);
  const [taskText, setTaskText] = useState('');
  const [taskHeading, setTaskHeading] = useState('');
  const [taskStatus, setTaskStatus] = useState('');

  
  const loadTasks = useCallback(async () => {
    const container = document.getElementById('tasks-container');
    if (!container) {
      return;
    }

    container.innerHTML = '';

    if (!isAuthenticated) {
      return;
    }

    try {
      const res = await api.get('/tasks/', { withCredentials: true });
      const tasks = res.data?.tasks ?? res.data ?? [];
      if (!Array.isArray(tasks) || tasks.length === 0) {
        const empty = document.createElement('div');
        empty.className = 'input-row';
        empty.textContent = 'No tasks found';
        container.appendChild(empty);
        return;
      }
      tasks.forEach((t) => {
        const id = t?.id ?? t?.task_id ?? t?.taskId;
        const title = t?.title ?? t?.name ?? '(no title)';
        const completed = t?.status === 'completed' || t?.completed === true;
        const row = document.createElement('div');
        row.className = 'input-row';
        const label = document.createElement('span');
        label.style.margin = '0 8px';
        label.textContent = title;
        const checkbox = document.createElement('button');
        checkbox.className = 'save-btn';
        checkbox.textContent = completed ? 'Completed' : 'Task Done';
        checkbox.title = completed ? 'Task already completed' : 'Mark task as done';
        checkbox.disabled = !!completed;
        checkbox.onclick = async () => {
          try {
            await api.put(`/tasks/${id}/complete`, {}, { withCredentials: true });
            checkbox.textContent = 'Completed';
            checkbox.disabled = true;
          } catch (error) {
            alert(error.response?.data?.detail ?? error.message ?? 'Failed to mark task as done');
          }
        };
        const del = document.createElement('button');
        del.className = 'save-btn';
        del.textContent = 'Delete';
        del.title = 'Delete task';
        del.onclick = async () => {
          try {
            await api.delete(`/tasks/${id}`, { withCredentials: true });
            row.remove();
          } catch (error) {
            alert(error.response?.data?.detail ?? error.message ?? 'Failed to delete task');
          }
        };
        row.appendChild(label);
        row.appendChild(checkbox);
        row.appendChild(del);
        container.appendChild(row);
      });
    } catch (error) {
      alert(error.response?.data?.detail ?? error.message ?? 'Failed to load tasks');
    }
  }, [isAuthenticated]);

  const authBaseUrl = api.defaults.baseURL ?? 'http://localhost:8000';

  // Check if user is authenticated and load their profile
  const checkAuthStatus = useCallback(async () => {
    setIsCheckingAuth(true);
    setAuthError('');
    try {
      const statusRes = await api.get('/auth/status', { withCredentials: true });
      console.log('Auth status response:', statusRes.data);
      if (statusRes.data?.authenticated) {
        setIsAuthenticated(true);
        try {
          const userRes = await api.get('/user/me', { withCredentials: true });
          const email = userRes.data?.email ?? userRes.data?.name ?? '';
          const uname = userRes.data?.name ?? '';
          setusername(uname);
          setUserEmail(email);
        } catch (userErr) {
          console.error('Fetching user profile failed:', userErr);
          setAuthError(userErr.response?.data?.detail ?? 'Unable to load user profile');
        }
        return;
      }
      setIsAuthenticated(false);
      setUserEmail('');
      setusername('');
    } catch (error) {
      console.error('Auth status check failed:', error);
      setIsAuthenticated(false);
      setUserEmail('');
      setAuthError(error.response?.data?.detail ?? 'Authentication check failed');
    } finally { 
      setIsCheckingAuth(false);
    }
  }, []);

  // Handle Google Login - redirect to FastAPI OAuth endpoint
  const handleGoogleLogin = async () => {
    // Redirect to your FastAPI Google OAuth endpoint
    window.location.href = `${authBaseUrl}/auth/login`;
  };

  const handleLogout = async () => {
    try {
      await api.post('/auth/logout', {}, { withCredentials: true });
    } catch (error) {
      console.error('Logout failed:', error);
      setAuthError(error.response?.data?.detail ?? 'Logout failed');
    } finally {
      setIsAuthenticated(false);
      setUserEmail('');
      checkAuthStatus();
    }
  };

  const refreshUpcomingEvents = useCallback(async () => {
    if (!isAuthenticated) {
      setUpcomingEvents([]);
      setEventsError('');
      setIsLoadingEvents(false);
      return;
    }

    setIsLoadingEvents(true);
    setEventsError('');
    try {
      const res = await api.get('/calendar/events', { withCredentials: true });
      const events = res.data?.events ?? res.data ?? [];
      const now = new Date();
      const end = new Date(now);
      end.setDate(end.getDate() + 7);

      const filtered = events
        .map((event) => {
          const raw = event?.start?.dateTime ?? event?.start?.date ?? event?.startDate;
          if (!raw) return null;

          const isAllDay = Boolean(event?.start?.date || (event?.startDate && !event?.start?.dateTime));
          const date = isAllDay ? new Date(`${raw}T00:00:00`) : new Date(raw);
          if (Number.isNaN(date.getTime())) return null;

          const labelDate = date.toLocaleDateString();
          const labelTime = isAllDay ? '' : date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
          const title = event?.summary ?? event?.title ?? '(no title)';

          return {
            id: event?.id ?? event?.eventId ?? `${title}-${date.toISOString()}`,
            label: `${labelDate}${labelTime ? ` ${labelTime}` : ''} - ${title}`,
            date,
          };
        })
        .filter(Boolean)
        .filter(({ date }) => date >= now && date <= end)
        .sort((a, b) => a.date.getTime() - b.date.getTime())
        .map(({ id, label }) => ({ id, label }));

      if (filtered.length === 0) {
        setUpcomingEvents([]);
        setEventsError('No events in the next 7 days');
      } else {
        setUpcomingEvents(filtered);
        setEventsError('');
      }
    } catch (error) {
      console.error('Failed to load events:', error);
      const message = error.response?.data?.detail ?? error.message ?? 'Failed to load events';
      setUpcomingEvents([]);
      setEventsError(message);
    } finally {
      setIsLoadingEvents(false);
    }
  }, [isAuthenticated]);

  const handleTaskSave = async () => {
    if (!isAuthenticated) {
      setTaskStatus('Please login with Google first.');
      return;
    }
    const head = taskHeading.trim();
    const text = taskText.trim();//here is a trim and store only trimed text 
    if (!head) {
      setTaskStatus('Please enter a task headline.');
      return;
    }
    if (!text) {
      setTaskStatus('Please enter a task.');
      return;
    }

    setTaskStatus('Saving task...');
    const endpointsToTry = ['/tasks/'];
    let saved = false;
    let lastError = null;

    for (const url of endpointsToTry) {
      try {
        const res = await api.post(url, {
          "title": head,
          "notes": text,
          "task_list_id": "@default"
        }, { withCredentials: true });
        if (res && res.status >= 200 && res.status < 300) {
          saved = true;
          break;
        }
      } catch (err) {
        lastError = err;
      }
    }

    if (saved) {
      setTaskStatus('Task saved successfully.');
      setTaskText('');
      setTaskHeading('');
      await loadTasks();
    } else {
      const msg = lastError?.response?.data?.detail ?? lastError?.message ?? 'Failed to save task';
      setTaskStatus(msg);
    }
  };

  useEffect(() => {
    checkAuthStatus();
  }, [checkAuthStatus]);

  useEffect(() => {
    if (isAuthenticated) {
      refreshUpcomingEvents();
      loadTasks();
    } else {
      setUpcomingEvents([]);
      setEventsError('');
      setTaskText('');
      setTaskStatus('');
      loadTasks();
    }
  }, [isAuthenticated, refreshUpcomingEvents, loadTasks]);
  return (
    <div className="dashboard-container">
      {/* Navigation */}
      <nav className="navbar">
        <div className="nav-links">
          <a href="#">Home</a>
          <a href="#">About Us</a>
          <a href="#">Contact Us</a>
        </div>
        <div className="logo">EvenetX</div>
        <div className="Login">
          {isCheckingAuth ? (
            <span>Checking session...</span>
          ) : isAuthenticated ? (
            <div className="auth-status">
              <span>{userName || 'Authenticated user'}</span>
              <button className="login-btn" onClick={handleLogout}>Logout</button>
            </div>
          ) : (
            <button className="login-btn" onClick={handleGoogleLogin}>Login with Google</button>
          )}
          {authError && !isCheckingAuth && (
            <span className="auth-error">{authError}</span>
          )}
        </div>
      </nav>

      {/* Hero Section */}
      <header className="hero">
        <h1>EvenetX a google Workspace Hub</h1>
        <p>Make all Events at one place</p>
      </header>

      {/* Content Grid */}
      <main className="grid-layout">
        <section className="card-section">
          <h2>Create Event</h2>
          <form
            className="card create-event-card"
            onSubmit={async (e) => {
              e.preventDefault();
              if (!isAuthenticated) {
                alert('Please login with Google first.');
                return;
              }
              const fd = new FormData(e.currentTarget);
              const summary = (fd.get('summary') || '').toString().trim();
              const description = (fd.get('description') || '').toString().trim();
              const location = (fd.get('location') || '').toString().trim();
              const attendeesRaw = (fd.get('attendees') || '').toString();
              const startDate = (fd.get('startDate') || '').toString();
              const endDateInput = (fd.get('endDate') || '').toString();
              const startTimeInput = (fd.get('startTime') || '').toString();
              const endTimeInput = (fd.get('endTime') || '').toString();

              const normalizeTime = (value) => {
                const trimmed = (value || '').toString().trim();
                if (!trimmed) {
                  return '00:00:00';
                }
                return trimmed.length === 5 ? `${trimmed}:00` : trimmed;
              };

              if (!summary || !startDate) {
                alert('Please enter event summary and start date.');
                return;
              }

              const startTime = normalizeTime(startTimeInput);
              const startDateTime = `${startDate}T${startTime}`;

              let endDate = endDateInput || startDate;
              let endTime = normalizeTime(endTimeInput || startTimeInput);

              const startInstant = new Date(`${startDate}T${startTime}`);
              let endInstant = new Date(`${endDate}T${endTime}`);

              if (Number.isNaN(startInstant.getTime())) {
                alert('Please enter a valid start date and time.');
                return;
              }

              if (Number.isNaN(endInstant.getTime()) || endInstant < startInstant) {
                endDate = startDate;
                endTime = startTime;
                endInstant = new Date(`${endDate}T${endTime}`);
              }

              const endDateTime = `${endDate}T${endTime}`;

              const attendees = attendeesRaw
                .split(/[,;\s]+/)
                .map((e) => e.trim())
                .filter(Boolean);

              const eventPayload = {
                summary,
                start_datetime: startDateTime,
                end_datetime: endDateTime,
                description,
                location,
                attendees,
                timezone: 'IST',
              };

              const endpointsToTry = [
                '/calendar/events',
              ];

              let created = false;
              let lastError = null;

              for (const url of endpointsToTry) {
                try {
                  const res = await api.post(url, eventPayload, { withCredentials: true });
                  if (res && (res.status >= 200 && res.status < 300)) {
                    created = true;
                    break;
                  }
                } catch (err) {
                  lastError = err;
                }
              }

              if (created) {
                alert('Event created successfully.');
                e.currentTarget.reset();
                await refreshUpcomingEvents();
              } else {
                const msg =
                  lastError?.response?.data?.detail ||
                  lastError?.message ||
                  'Failed to create event';
                alert(msg);
              }
            }}
          >
            <div className="input-row">
              <input name="summary" type="text" placeholder="Event Summary" />
            </div>
            <div className="input-row">
              <span>StartEvent:</span>
              <input className="startDate" name="startDate" type="date" style={{ width: '25%' }} />
              <span>StartTime:</span>
              <input className="startTime" name="startTime" type="time" />
            </div>
            <div className="input-row">
              <span>End Event:</span>
              <input className="endDate" name="endDate" type="date" style={{ width: '25%' }} />
              <span>End Time:</span>
              <input className="endTime" name="endTime" type="time" />
            </div>
            <div className="input-row">
              <input name="description" type="text" placeholder="Description" />
            </div>
            <div className="input-row">
              <input
                name="attendees"
                type="text"
                placeholder="Attendee emails"
                title="You can add multiple emails separated by commas"
              />
            </div>
            <div className="input-row">
              <input name="location" type="text" placeholder="Location" />
            </div>
            <button className="save-btn" type="submit" disabled={!isAuthenticated} title={isAuthenticated ? 'Create event' : 'Login required'}>
              Save
            </button>
          </form>

          <section className="clock-section">
            <h2>Clock</h2>
            <div className="card clock-card">
              <iframe
                src="https://free.timeanddate.com/clock/ia7w4kyf/n54/tlin/fn7/fs20/fce9b36b/tct/pct/ftb/th2/ta1"
                width="176"
                height="90"
                allowTransparency="true"
              ></iframe>
            </div>
          </section>
        </section>

        <section className="card-section">
          <h2>Calendar</h2>
          <div className="card calendar-card">
            <Calendar />
          </div>
        </section>

        <div className="card-section full-width">
          <h2>Upcoming Events</h2>
          <div className="eventmanegament">
            <div className="card upcoming-card">
              <div className="placeholder-content" style={{ marginBottom: '-2rem' }}>
                {!isAuthenticated && <span>Login to see events</span>}
                {isAuthenticated && (
                  <>
                    {isLoadingEvents && <span>Loading...</span>}
                    {!isLoadingEvents && eventsError && <span className="auth-error">{eventsError}</span>}
                    {!isLoadingEvents && !eventsError && upcomingEvents.length === 0 && (
                      <span>No events in the next 7 days</span>
                    )}
                    {!isLoadingEvents && !eventsError && upcomingEvents.length > 0 && (
                      <div className="upcoming-events-list">
                        {upcomingEvents.map(({ id, label }) => (
                          <div key={id} className="input-row">{label}</div>
                        ))}
                      </div>
                    )}
                  </>
                )}
              </div>
              <div className="buttionname" style={{ marginTop: '6px' }}>
                <button
                  type="button"
                  className="save-btn"
                  onClick={refreshUpcomingEvents}
                  disabled={!isAuthenticated || isLoadingEvents}
                  title={isAuthenticated ? 'Refresh events' : 'Login required'}
                >
                  Refresh
                </button>
              </div>
            </div>
            <div className='taskshow'>
              <section className='TaskShow'>
                <h2>Upcoming Task</h2>
                <div className="card taskshow-card">
                  <div id="tasks-container" className="upcoming-events-list" style={{ marginBottom: '8px' }}></div>
                </div>
              </section>
            </div>
          </div>
        </div >
        <section className="card-section full-width">
          <h2>Your Tasks</h2>
          <div className="card notes-card">
            <div className='input-row'>
              <input type="text"
                placeholder="Enter Task Headline"
                value={taskHeading}
                onChange={(e) => setTaskHeading(e.target.value)}
              />
            </div>
            <textarea
              id="task-text"
              placeholder="Write your event Tasks here..."
              value={taskText}
              onChange={(e) => setTaskText(e.target.value)}
            ></textarea>
            {taskStatus && (
              <div
                style={{
                  marginTop: '8px',
                  color:
                    taskStatus === 'Task saved successfully.'
                      ? '#1b5e20'
                      : taskStatus === 'Saving task...'
                        ? '#1976d2'
                        : '#d32f2f',
                }}
              >
                {taskStatus}
              </div>
            )}
            <div className="input" style={{ marginTop: '8px' }}>
              <button
                type="button"
                className="save-btn"
                onClick={handleTaskSave}
                disabled={!isAuthenticated}
                title={isAuthenticated ? 'Save task' : 'Login required'}
              >
                Save Task
              </button>
            </div>
          </div>
        </section>
        <section>
          <h2>Your Task Assistence</h2>
          <div className="card ai-response-card">

          </div>
        </section>
      </main >
      {/* Footer */}
      <footer footer className="footer" >
        <div className="footer-content">
          <div className="sitemap">
            <p>SITEMAP</p>
            <div className="socials">FB IG TW LI</div>
          </div>
          <div className="footer-links">
            <span>MENU</span>
            <span>SERVICES</span>
            <span>LEGAL</span>
          </div>
        </div>
      </footer >
    </div >
  );
};

export default App; 
