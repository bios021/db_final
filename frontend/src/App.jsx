import React, { useState } from 'react';
import LoginView from './component/login';
import DashboardView from './component/dashboard';
import './App.css';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [studentId, setStudentId] = useState('');

  return (
    <div className={isLoggedIn ? "app-container-full" : "app-container-login"}>
      {isLoggedIn ? (
        <DashboardView setIsLoggedIn={setIsLoggedIn} studentId={studentId} />
      ) : (
        <LoginView setIsLoggedIn={setIsLoggedIn} setStudentId={setStudentId} />
      )}
    </div>
  );
}

export default App;
