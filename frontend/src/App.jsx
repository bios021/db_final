import React, { useState } from 'react';
import LoginView from './component/login';       // 💡 注意：如果你資料夾叫 components，這裡要改成 components
import DashboardView from './component/dashboard';
import './App.css';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [studentId, setStudentId] = useState('');

  return (
    <div className="app-container">
      {isLoggedIn ? (
        <DashboardView setIsLoggedIn={setIsLoggedIn} studentId={studentId} />
      ) : (
        // 🎯 把控制權跟學號狀態，丟給登入頁面去處理
        <LoginView setIsLoggedIn={setIsLoggedIn} setStudentId={setStudentId} />
      )}
    </div>
  );
}


export default App;
