import React from 'react';
import { Link } from 'react-router-dom';
import './styles.scss';

const Navigation = () => {
  return (
    <nav className="main-nav">
      <ul>
        <li>
          <Link to="/">Generate Icons</Link>
        </li>
        <li>
          <Link to="/train">Train Model</Link>
        </li>
      </ul>
    </nav>
  );
};

export default Navigation; 