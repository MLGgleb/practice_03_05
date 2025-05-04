import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import './App.css';
import RequestsPage from './RequestsPage';
import Home from './Home';

function MainRouter() {
  return (
    <Router>
      <nav className="navbar">
        <Link to="/" className="nav-link">Главная</Link>
        <Link to="/requests" className="nav-link">История Запросов</Link>
      </nav>

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/requests" element={<RequestsPage />} />
      </Routes>
    </Router>
  );
}

export default MainRouter;