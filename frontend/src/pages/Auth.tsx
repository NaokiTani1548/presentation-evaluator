import React, { useState } from 'react';
import { Box, Card, CardContent, Tabs, Tab, TextField, Button, Typography, Alert } from '@mui/material';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import { useNavigate } from 'react-router-dom';

interface AuthProps {
  onSigninSuccess?: (user: { user_id: string; user_name: string; email_address: string }) => void;
}

const Auth: React.FC<AuthProps> = ({ onSigninSuccess }) => {
  const [tab, setTab] = useState(0);
  // サインアップ用
  const [signupName, setSignupName] = useState('');
  const [signupEmail, setSignupEmail] = useState('');
  const [signupPassword, setSignupPassword] = useState('');
  const [signupResult, setSignupResult] = useState<string | null>(null);
  // サインイン用
  const [signinId, setSigninId] = useState('');
  const [signinPassword, setSigninPassword] = useState('');
  const [signinResult, setSigninResult] = useState<string | null>(null);
  const [userInfo, setUserInfo] = useState<any>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [dialogMsg, setDialogMsg] = useState('');
  const navigate = useNavigate();

  const handleSignup = async () => {
    setSignupResult(null);
    try {
      const formData = new FormData();
      formData.append('user_name', signupName);
      formData.append('email_address', signupEmail);
      formData.append('password', signupPassword);
      const res = await fetch('http://127.0.0.1:8000/users/signup', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (data && data.user_id) {
        setSignupResult(`登録成功！あなたのユーザーID: ${data.user_id} \n サインインに必要なので忘れないように保存してください`);
      } else {
        setDialogMsg('登録に失敗しました');
        setOpenDialog(true);
      }
    } catch {
      setDialogMsg('通信エラー');
      setOpenDialog(true);
    }
  };

  const handleSignin = async () => {
    setSigninResult(null);
    setUserInfo(null);
    try {
      const formData = new FormData();
      formData.append('user_id', signinId);
      formData.append('password', signinPassword);
      const res = await fetch('http://127.0.0.1:8000/users/signin', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (data && data.user_id) {
        setUserInfo(data);
        setSigninResult('サインイン成功');
        if (onSigninSuccess) onSigninSuccess({
          user_id: data.user_id,
          user_name: data.user_name,
          email_address: data.email_address
        });
        setTimeout(() => navigate('/Home'), 500); // 0.5秒後にページ遷移
      } else {
        setDialogMsg('ユーザーIDまたはパスワードが間違っています');
        setOpenDialog(true);
      }
    } catch {
      setDialogMsg('通信エラー');
      setOpenDialog(true);
    }
  };

  return (
    <Box sx={{ display: 'flex', justifyContent: 'center', mt: 8 }}>
      <Card sx={{ minWidth: 350, maxWidth: 400 }}>
        <CardContent>
          <Tabs value={tab} onChange={(_, v) => setTab(v)} centered>
            <Tab label="サインイン" />
            <Tab label="サインアップ" />
          </Tabs>
          {tab === 0 && (
            <Box sx={{ mt: 2 }}>
              <TextField label="ユーザーID" fullWidth margin="normal" value={signinId} onChange={e => setSigninId(e.target.value)} required />
              <TextField label="パスワード" type="password" fullWidth margin="normal" value={signinPassword} onChange={e => setSigninPassword(e.target.value)} required />
              <Button variant="contained" fullWidth sx={{ mt: 2 }} onClick={handleSignin} disabled={!signinId || !signinPassword}>サインイン</Button>
              {signinResult && <Alert severity={userInfo ? 'success' : 'error'} sx={{ mt: 2 }}>{signinResult}</Alert>}
              {userInfo && (
                <Box sx={{ mt: 2 }}>
                  <Typography>ユーザー名: {userInfo.user_name}</Typography>
                  <Typography>メール: {userInfo.email_address}</Typography>
                </Box>
              )}
            </Box>
          )}
          {tab === 1 && (
            <Box sx={{ mt: 2 }}>
              <TextField label="ユーザー名" fullWidth margin="normal" value={signupName} onChange={e => setSignupName(e.target.value)} required />
              <TextField label="メールアドレス" fullWidth margin="normal" value={signupEmail} onChange={e => setSignupEmail(e.target.value)} required />
              <TextField label="パスワード" type="password" fullWidth margin="normal" value={signupPassword} onChange={e => setSignupPassword(e.target.value)} required />
              <Button variant="contained" fullWidth sx={{ mt: 2 }} onClick={handleSignup} disabled={!signupName || !signupEmail || !signupPassword}>サインアップ</Button>
              {signupResult && <Alert severity={signupResult.includes('成功') ? 'success' : 'error'} sx={{ mt: 2 }}>{signupResult}</Alert>}
            </Box>
          )}
        </CardContent>
      </Card>
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)}>
        <DialogTitle>エラー</DialogTitle>
        <DialogContent>
          <Typography>{dialogMsg}</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>閉じる</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Auth;
