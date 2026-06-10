import React, { useState, useEffect } from 'react';

function DashboardView({ setIsLoggedIn, studentId }) {
  const [activeTab, setActiveTab] = useState('courses');
  const [creditData, setCreditData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [checkResult, setCheckResult] = useState(null);
  const [checking, setChecking] = useState(false);
  const [checkError, setCheckError] = useState('');

  // 修課紀錄
  useEffect(() => {
    const fetchCourses = async () => {
      try {
        const token = localStorage.getItem('token');
        //改為讀取 Vite 環境變數
        const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/students/me/courses`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) {
          setError('無法取得修課資料');
          return;
        }
        const data = await response.json();
        setCreditData(data.data ?? []);
      } catch (err) {
        setError('連線伺服器失敗');
      } finally {
        setLoading(false);
      }
    };
    fetchCourses();
  }, [studentId]);

  // 學分檢核
  const handleCheck = async () => {
    setChecking(true);
    setCheckResult(null);
    setCheckError('');
    try {
      const token = localStorage.getItem('token');
      //改為讀取 Vite 環境變數
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/graduation/audit`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!response.ok) {
        setCheckError('無法取得檢核結果');
        return;
      }
      const data = await response.json();
      setCheckResult(data);
    } catch (err) {
      setCheckError('連線伺服器失敗');
    } finally {
      setChecking(false);
    }
  };

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    if (tab === 'check' && !checkResult) {
      handleCheck();
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsLoggedIn(false);
  };

  return (
    <div className="app-container-full">
      <div className="sidebar">
        <div className="sidebar-title">學分檢核系統</div>
        <div className="student-info">學號：{studentId}</div>

        <button
          onClick={() => handleTabChange('courses')}
          className={`nav-button ${activeTab === 'courses' ? 'active' : ''}`}
        >
          修課紀錄
        </button>

        <button
          onClick={() => handleTabChange('check')}
          className={`nav-button ${activeTab === 'check' ? 'active' : ''}`}
        >
          學分檢核
        </button>

        <button onClick={handleLogout} className="logout-button">
          登出
        </button>
      </div>

      <div className="dashboard-content-area">
        <div className="dashboard-card">

          {/* 修課紀錄 */}
          {activeTab === 'courses' && (
            <div>
              <h3 className="content-title">修課紀錄</h3>
              {loading && <p style={{ color: '#94a3b8' }}>載入中...</p>}
              {error && <p style={{ color: '#e63946' }}>{error}</p>}
              {!loading && !error && (
                <table className="credit-table">
                  <thead>
                    <tr style={{ backgroundColor: '#f8fafc' }}>
                      <th>學期</th>
                      <th>課程名稱</th>
                      <th>學分</th>
                      <th>成績</th>
                      <th>狀態</th>
                    </tr>
                  </thead>
                  <tbody>
                    {creditData.map((item, idx) => (
                      <tr key={idx}>
                        <td>{item.semester}</td>
                        <td>{item.course_name}</td>
                        <td>{item.credits}</td>
                        <td>{item.grade ?? '--'}</td>
                        <td>
                          <span style={{
                            color: item.grade === null ? '#94a3b8' : item.grade >= 60 ? '#2ec4b6' : '#e63946',
                            fontWeight: '600'
                          }}>
                            {item.grade === null ? '修習中' : item.grade >= 60 ? '已通過' : '未通過'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          )}

          {/* 學分檢核 */}
          {activeTab === 'check' && (
            <div>
              <h3 className="content-title">畢業學分檢核</h3>
              {checking && <p style={{ color: '#94a3b8' }}>檢核中...</p>}
              {checkError && <p style={{ color: '#e63946' }}>{checkError}</p>}
              {!checking && checkResult && (
                <>
                  {/* 整體狀態 */}
                  <div style={{
                    padding: '12px 16px',
                    borderRadius: '8px',
                    marginBottom: '16px',
                    backgroundColor: checkResult.is_graduable ? '#d1fae5' : '#fee2e2',
                    color: checkResult.is_graduable ? '#065f46' : '#dc2626',
                    fontWeight: '600'
                  }}>
                    {checkResult.is_graduable ? '✅ 已達畢業門檻' : '❌ 尚未達到畢業門檻'}
                    　總計：{checkResult.total_earned} / {checkResult.total_required} 學分
                  </div>

                  {/* 各條件細項 */}
                  {checkResult.summary_by_conditions.map((cond, idx) => (
                    <div key={idx} className="rule-card">
                      <div className="rule-header">
                        <span style={{ fontWeight: '600', color: '#334155' }}>{cond.condition_name}</span>
                        <span style={{
                          color: cond.status === 'COMPLETED' ? '#2ec4b6' : '#e63946',
                          fontWeight: '600'
                        }}>
                          {cond.earned_credits} / {cond.required_credits} 學分
                          {cond.status === 'COMPLETED' ? ' ✓' : ' ✗'}
                        </span>
                      </div>
                      <div className="progress-bar">
                        <div className="progress-fill" style={{
                          width: `${Math.min(cond.earned_credits / cond.required_credits * 100, 100)}%`,
                          backgroundColor: cond.status === 'COMPLETED' ? '#2ec4b6' : '#f59e0b'
                        }} />
                      </div>
                      {cond.details.map((d, dIdx) => (
                        <div key={dIdx} className="condition-row">
                          <span style={{ fontSize: '13px', color: '#64748b' }}>　{d}</span>
                        </div>
                      ))}
                    </div>
                  ))}

                  {/* 未對應課程 */}
                  {checkResult.unmapped_courses.length > 0 && (
                    <div className="rule-card">
                      <div style={{ fontWeight: '600', color: '#334155', marginBottom: '8px' }}>
                        未對應課程
                      </div>
                      {checkResult.unmapped_courses.map((c, idx) => (
                        <div key={idx} style={{ fontSize: '13px', color: '#94a3b8', padding: '4px 0' }}>
                          　{c}
                        </div>
                      ))}
                    </div>
                  )}
                </>
              )}
            </div>
          )}

        </div>
      </div>
    </div>
  );
}

export default DashboardView;
