import React, { useState } from 'react';

function LoginView({ setIsLoggedIn, setStudentId }) {
  const [inputState, setInputState] = useState({ id: '', pwd: '' });
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!inputState.id || !inputState.pwd) {
      setMessage('⚠️ 請填寫學號與密碼！');
      return;
    }

    try {
      const response = await fetch('http://localhost:8080/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ student_id: inputState.id, password: inputState.pwd }),
      });

      if (response.ok) {
	const data = await response.json()  // 拿到後端回傳的資料
        localStorage.setItem('token', data.token)  // 存 token
        setStudentId(inputState.id);
        setIsLoggedIn(true);
      } else {
        setMessage('登入失敗: 帳號或密碼錯誤');
      }
    } catch (error) {
      setMessage('連線伺服器失敗');
      console.error('Error:', error);
    }
  };

  return (
    <div className="login-card">
      <h2 className="login-title">學分檢核系統</h2>
      <p className="login-subtitle">請輸入您的校務帳號以開始檢核</p>
      
      <form onSubmit={handleSubmit} className="login-form">
        <div className="input-group">
          <label className="input-label">學號</label>
          <input
            type="text"
            placeholder="請輸入學號"
            value={inputState.id}
            onChange={(e) => setInputState({ ...inputState, id: e.target.value })}
            className="login-input"
          />
        </div>
        
        <div className="input-group">
          <label className="input-label">密碼</label>
          <input
            type="password"
            placeholder="請輸入密碼"
            value={inputState.pwd}
            onChange={(e) => setInputState({ ...inputState, pwd: e.target.value })}
            className="login-input"
          />
        </div>
        
        <button type="submit" className="login-button">
          登入
        </button>
      </form>
      
      {message && (
        <div className="message-box" style={{ color: message.includes('成功') ? '#2ec4b6' : '#e63946' }}>
          {message}
        </div>
      )}
    </div>
  );
}

export default LoginView;
