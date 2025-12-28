import React from 'react';
import './App.css';
import Calendar from './Calendar.jsx';

const EvenetX = () => {
  return (
    <div className="dashboard-container">
      {/* Navigation */}
      <nav className="navbar">
        <div className="nav-links">
          <a href="#">Home</a>
          <a href="#">Event</a>
          <a href="#">About Us</a>
          <a href="#">Contact Us</a>
        </div>
        <div className="logo">EvenetX</div>
        <div className="Login"></div>
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
          <div className="card create-event-card">
            <div className="input-row">
              <input type="text" placeholder="Event Title" />
            </div>
            <div className="input-row">
              <span>StartEvent:</span>
              <input type="date" />
            </div>
            <div className="input-row">
              <span>End Event:</span>
              <input type="date" />
            </div>
            <div className="input-row">
              <input type="email" placeholder="Enter a email to notify" />
              <button className="add-email-btn">Add</button>
            </div>
            <div className='input-row'>
              <input type="text" placeholder="location" />
                <button className="add-email-btn">Add</button>
            </div>
            <button className="save-btn">Save </button>
          </div>
        </section>

        <section className="card-section">
          <h2>Calendar</h2>
          <div className="card calendar-card">
              <Calendar />
          </div>
        </section>

        <section className="card-section full-width">
          <h2>Upcoming Event</h2>
          <div className="card upcoming-card">
            <div className="placeholder-content">
              <span>Drag events here to schedule</span>
            </div>
          </div>
        </section>

        <section className="card-section full-width">
          <h2>Yours Notes</h2>
          <div className="card notes-card">
            <textarea placeholder="Write your event notes here..."></textarea>
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

export default EvenetX;