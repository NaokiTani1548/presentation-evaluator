import React from 'react';

const user_id = localStorage.getItem('user_id');
const user_name = localStorage.getItem('user_name');
const email_address = localStorage.getItem('email_address');

const Index: React.FC = () => {
  return (
    <div>
      <h1>Welcome to the Presentation Review Meeting ver1.0</h1>
    </div>
  );
};

export default Index;