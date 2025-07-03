import React from 'react';

const user_id = localStorage.getItem('user_id');
const user_name = localStorage.getItem('user_name');
const email_address = localStorage.getItem('email_address');

const Log: React.FC = () => {
  return (
    <div>
      <h1>State Page</h1>
      <p>This is the main content of the home page.</p>
    </div>
  );
};

export default Log;