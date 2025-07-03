import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import Layout from './components/Layout';
import Auth from './pages/Auth';
import Home from './pages/Route';
import Review from './pages/Review';
import Log from './pages/Log';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import Button from '@mui/material/Button';

const isAuthenticated = () => {
  return !!localStorage.getItem('user_id');
};

const PrivateRoute = () => {
  return isAuthenticated() ? <Outlet /> : <Navigate to="/" replace />;
};

function withAuthGuard<P extends object>(Component: React.ComponentType<P>) {
  return function AuthGuardedComponent(props: P) {
    const user_id = localStorage.getItem('user_id');
    const [open, setOpen] = React.useState(!user_id);
    if (!user_id) {
      return (
        <Dialog open={open}>
          <DialogTitle>認証エラー</DialogTitle>
          <DialogContent>ログインしてください</DialogContent>
          <DialogActions>
            <Button onClick={() => window.location.href = '/'}>ログイン画面へ</Button>
          </DialogActions>
        </Dialog>
      );
    }
    return <Component {...props} />;
  };
}

const GuardedHome = withAuthGuard(Home);
const GuardedReview = withAuthGuard(Review);
const GuardedLog = withAuthGuard(Log);

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<AuthWrapper />} />
        <Route element={<PrivateRoute />}>
          <Route element={<Layout><Outlet /></Layout>}>
            <Route path="/Home" element={<GuardedHome />} />
            <Route path="/Review" element={<GuardedReview />} />
            <Route path="/log" element={<GuardedLog />} />
          </Route>
        </Route>
      </Routes>
    </Router>
  );
}

function AuthWrapper() {
  // サインイン成功時にuser情報をlocalStorageへ保存
  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #e3f0ff 0%, #fafcff 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
    }}>
      <Auth onSigninSuccess={user => {
        localStorage.setItem('user_id', user.user_id);
        localStorage.setItem('user_name', user.user_name);
        localStorage.setItem('email_address', user.email_address);
      }} />
    </div>
  );
}

export default App;