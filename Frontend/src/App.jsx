import './App.css';
import Calendar from './Calendar.jsx';
import React, { useState, useEffect, useCallback } from 'react';
import api from './api';




const App = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userEmail, setUserEmail] = useState('');
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);
  const [authError, setAuthError] = useState('');
  const [upcomingEvents, setUpcomingEvents] = useState([]);
  const [eventsError, setEventsError] = useState('');
  const [isLoadingEvents, setIsLoadingEvents] = useState(false);
  const [taskText, setTaskText] = useState('');
  const [taskStatus, setTaskStatus] = useState('');

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
          setUserEmail(email);
        } catch (userErr) {
          console.error('Fetching user profile failed:', userErr);
          setAuthError(userErr.response?.data?.detail ?? 'Unable to load user profile');
        }
        return;
      }
      setIsAuthenticated(false);
      setUserEmail('');
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

    const text = taskText.trim();
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
          "title": "Task from EvenetX",
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
    } else {
      setUpcomingEvents([]);
      setEventsError('');
      setTaskText('');
      setTaskStatus('');
    }
  }, [isAuthenticated, refreshUpcomingEvents]);
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
              <span>{userEmail || 'Authenticated user'}</span>
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
        <p>Make all google project at one place</p>
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
              const title = (fd.get('title') || '').toString().trim();
              let startDate = (fd.get('startDate') || '').toString();
              let endDate = (fd.get('endDate') || '').toString();
              const attendeesRaw = (fd.get('attendees') || '').toString();
              const location = (fd.get('location') || '').toString().trim();

              if (!title || !startDate) {
                alert('Please enter event title and start date.');
                return;
              }

              if (!endDate) endDate = startDate;
              if (endDate < startDate) endDate = startDate;

              const attendees = attendeesRaw
                .split(/[,;\s]+/)
                .map((e) => e.trim())
                .filter(Boolean)
                .map((email) => ({ email }));

              const eventPayload = {
                title,
                location,
                startDate,
                endDate,
                attendees: attendees.map(a => a.email),
                // Common Google Calendar event shape
                event: {
                  summary: title,
                  location,
                  start: { date: startDate },
                  end: { date: endDate },
                  attendees,
                },
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
                  // try next endpoint
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
              <input name="title" type="text" placeholder="Event Title" />
            </div>
            <div className="input-row">
              <span>Start Event:</span>
              <input name="startDate" type="date" />
            </div>
            <div className="input-row">
              <span>End Event:</span>
              <input name="endDate" type="date" />
            </div>
            <div className="input-row">
              <input
                name="attendees"
                type="text"
                placeholder="Attendee emails "
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

        <section className="card-section full-width">
          <h2>Upcoming Events</h2>
          <div className="card upcoming-card">
            <div className="placeholder-content">
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
                        <div key={id} className="event-line">{label}</div>
                      ))}
                    </div>
                  )}
                </>
              )}
            </div>
            <div className="input-row" style={{ marginTop: '8px' }}>
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
        </section>
        <section className="card-section full-width">
          <h2>Your Tasks</h2>
          <div className="card notes-card">
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
            <div className="input-row" style={{ marginTop: '8px' }}>
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
      </main>
      {/* Footer */}
      <footer className="footer">
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
      </footer>
    </div>
  );
};

export default App; 
