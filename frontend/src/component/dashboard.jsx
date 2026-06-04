import React, { useState } from 'react';

function DashboardView({ setIsLoggedIn, studentId }) {
  const [creditData] = useState([
    { id: 1, name: '計算機概論', credit: 3, grade: 'A', status: '已通過' },
    { id: 2, name: '資料結構', credit: 3, grade: 'A-', status: '已通過' },
    { id: 3, name: '網頁前端開發', credit: 2, grade: 'B+', status: '已通過' },
    { id: 4, name: '資料庫系統', credit: 3, grade: '--', status: '修習中' },
  ]);

  return (
    <div style={styles.dashboardCard}>
      <div style={styles.dashboardHeader}>
        <h3 style={{ margin: 0 }}>📊 學分取得概況 (學生: {studentId})</h3>
        <button onClick={() => setIsLoggedIn(false)} style={styles.logoutBtn}>登出</button>
      </div>
      
      <table style={styles.table}>
        <thead>
          <tr style={{ backgroundColor: '#f8fafc' }}>
            <th style={styles.th}>課程名稱</th>
            <th style={styles.th}>學分</th>
            <th style={styles.th}>等第</th>
            <th style={styles.th}>狀態</th>
          </tr>
        </thead>
        <tbody>
          {creditData.map((item) => (
            <tr key={item.id}>
              <td style={styles.td}>{item.name}</td>
              <td style={styles.td}>{item.credit}</td>
              <td style={styles.td}>{item.grade}</td>
              <td style={styles.td}>{item.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

const styles = {
  dashboardCard: { padding: '35px', borderRadius: '16px', backgroundColor: '#fff', width: '550px', boxShadow: '0 10px 30px rgba(0,0,0,0.3)' },
  dashboardHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '25px', borderBottom: '2px solid #f1f5f9', paddingBottom: '12px' },
  logoutBtn: { padding: '6px 14px', backgroundColor: '#fee2e2', border: 'none', borderRadius: '6px', cursor: 'pointer', color: '#dc2626', fontWeight: '600' },
  table: { width: '100%', borderCollapse: 'collapse' },
  th: { textAlign: 'left', padding: '12px', fontSize: '14px', color: '#475569', borderBottom: '2px solid #e2e8f0' },
  td: { padding: '12px', fontSize: '14px', color: '#334155', borderBottom: '1px solid #f1f5f9' }
};

export default DashboardView;
