import React, { useState, useEffect } from 'react';

function DashboardView({ setIsLoggedIn, studentId }) {
  const [activeTab, setActiveTab] = useState('courses');
  const [creditData, setCreditData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [checkResult, setCheckResult] = useState(null);
  const [checking, setChecking] = useState(false);

  useEffect(() => {
    const mockData = [
      { course_id: 1, course_name: '計算機概論', credits: 3, grade: 85 },
      { course_id: 2, course_name: '資料結構', credits: 3, grade: 72 },
      { course_id: 3, course_name: '網頁前端開發', credits: 2, grade: 55 },
      { course_id: 4, course_name: '資料庫系統', credits: 3, grade: null },
    ];
    setCreditData(mockData);
    setLoading(false);
  }, [studentId]);

  const handleCheck = async () => {
    setChecking(true);
    setCheckResult(null);
    const mockCheckResult = {
      rules: [
        {
          rule_name: '專業必修規則',
          required_credits: 39,
          earned_credits: 20,
          is_satisfied: false,
          conditions: [
            { condition_name: '微積分甲', required_credits: 6, earned_credits: 6, is_satisfied: true },
            { condition_name: '線性代數', required_credits: 3, earned_credits: 0, is_satisfied: false },
            { condition_name: '資料結構', required_credits: 3, earned_credits: 3, is_satisfied: true },
          ]
        },
        {
          rule_name: '專業群修規則',
          required_credits: 12,
          earned_credits: 6,
          is_satisfied: false,
          conditions: [
            { condition_name: '群修A', required_credits: 6, earned_credits: 6, is_satisfied: true },
            { condition_name: '群修B', required_credits: 3, earned_credits: 0, is_satisfied: false },
            { condition_name: '群修C', required_credits: 3, earned_credits: 0, is_satisfied: false },
          ]
        },
        {
          rule_name: '通識規則',
          required_credits: 28,
          earned_credits: 3,
          is_satisfied: false,
          conditions: [
            { condition_name: '人文通識', required_credits: 3, earned_credits: 3, is_satisfied: true },
            { condition_name: '社會通識', required_credits: 3, earned_credits: 0, is_satisfied: false },
            { condition_name: '自然通識', required_credits: 3, earned_credits: 0, is_satisfied: false },
          ]
        }
      ]
    };
    await new Promise(resolve => setTimeout(resolve, 800));
    setCheckResult(mockCheckResult);
    setChecking(false);
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
          
          {activeTab === 'courses' && (
            <div>
              <h3 className="content-title">修課紀錄</h3>
              {loading ? (
                <p style={{ color: '#94a3b8' }}>載入中...</p>
              ) : (
                <table className="credit-table">
                  <thead>
                    <tr style={{ backgroundColor: '#f8fafc' }}>
                      <th className="credit-table th">課程名稱</th>
                      <th className="credit-table th">學分</th>
                      <th className="credit-table th">成績</th>
                      <th className="credit-table th">狀態</th>
                    </tr>
                  </thead>
                  <tbody>
                    {creditData.map((item) => (
                      <tr key={item.course_id}>
                        <td className="credit-table td">{item.course_name}</td>
                        <td className="credit-table td">{item.credits}</td>
                        <td className="credit-table td">{item.grade ?? '--'}</td>
                        <td className="credit-table td">
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

          {activeTab === 'check' && (
            <div>
              <h3 className="content-title">畢業學分檢核</h3>
              {checking ? (
                <p style={{ color: '#94a3b8' }}>檢核中...</p>
              ) : checkResult ? (
                checkResult.rules.map((rule, ruleIdx) => (
                  <div key={ruleIdx} className="rule-card">
                    <div className="rule-header">
                      <span style={{ fontWeight: '600', color: '#334155' }}>{rule.rule_name}</span>
                      <span style={{ color: rule.is_satisfied ? '#2ec4b6' : '#e63946', fontWeight: '600' }}>
                        {rule.earned_credits} / {rule.required_credits} 學分
                        {rule.is_satisfied ? ' [已達標]' : ' [未達標]'}
                      </span>
                    </div>
                    <div className="progress-bar">
                      <div className="progress-fill" style={{
                        width: `${Math.min(rule.earned_credits / rule.required_credits * 100, 100)}%`,
                        backgroundColor: rule.is_satisfied ? '#2ec4b6' : '#f59e0b'
                      }} />
                    </div>
                    {rule.conditions.map((cond, condIdx) => (
                      <div key={condIdx} className="condition-row">
                        <span style={{ color: '#64748b', fontSize: '13px' }}>
                          {cond.is_satisfied ? '[已達標]' : '[未達標]'} {cond.condition_name}
                        </span>
                        <span style={{ fontSize: '13px', color: '#64748b' }}>
                          {cond.earned_credits} / {cond.required_credits} 學分
                        </span>
                      </div>
                    ))}
                  </div>
                ))
              ) : null}
            </div>
          )}
          
        </div>
      </div>
    </div>
  );
}

export default DashboardView;
