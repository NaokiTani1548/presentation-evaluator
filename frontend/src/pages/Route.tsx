import React from 'react';
import agent from './agent.png';

const user_id = localStorage.getItem('user_id');
const user_name = localStorage.getItem('user_name');
const email_address = localStorage.getItem('email_address');

const Index: React.FC = () => {
  return (
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column', 
      justifyContent: 'center', 
      alignItems: 'center', 
      minHeight: '100vh', 
      background: '#fff',
      position: 'relative'
    }}>
      <h1 style={{ fontSize: '3.2rem', fontWeight: 'bold', marginBottom: '1.5rem', fontFamily: 'sans-serif', textAlign: 'center', letterSpacing: '0.04em' }}>
        Speech Coach
      </h1>
      <img
        src={agent}
        alt="AI Agent"
        style={{
          width: 340,
          height: 340,
          objectFit: 'contain',
          marginBottom: '1.8rem',
          display: 'block',
        }}
      />
      <div style={{ textAlign: 'center', fontSize: '1.5rem', fontWeight: 600, fontFamily: 'sans-serif', color: '#000', lineHeight: '2.4rem' }}>
        異なる専門性を持つAIが<br />
        あなたのプレゼンを成功へ導く
      </div>
      <div style={{
        position: 'absolute',
        bottom: 12,
        left: 0,
        width: '100%',
        textAlign: 'center',
        fontSize: '1rem',
        color: '#fff',
        fontWeight: 'bold',
        fontFamily: 'sans-serif',
        background: 'linear-gradient(90deg, #1976d2 0%, #42a5f5 100%)',
        padding: '0.5rem 0',
        letterSpacing: '0.05em',
        boxShadow: '0 2px 8px rgba(25, 118, 210, 0.15)',
        zIndex: 10,
        borderRadius: '8px',
        margin: '0 12px'
      }}>
        ← <span style={{ textDecoration: 'underline', textShadow: '0 2px 8px #1976d2' }}>Reviewタブ</span>からエージェントにアクセス
      </div>
    </div>
  );
};

export default Index;