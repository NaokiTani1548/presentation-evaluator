import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Card, CardContent, Typography, Box } from '@mui/material';

const user_id = localStorage.getItem('user_id');

interface LogItem {
  user_id: string;
  date: string;
  summary: string;
  structure_score: number;
  speech_score: number;
  knowledge_score: number;
  personas_score: number;
  comparison_score: number;
}

const Log: React.FC = () => {
  const [logData, setLogData] = useState<LogItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchLog = async () => {
      setLoading(true);
      setError(null);
      try {
        const formData = new FormData();
        formData.append('user_id', user_id || '');
        const res = await fetch('http://127.0.0.1:8000/analysis_results/get_by_user_id', {
          method: 'POST',
          body: formData,
        });
        if (!res.ok) throw new Error('API error');
        const data = await res.json();
        setLogData(data);
      } catch {
        setError('データ取得に失敗しました');
      } finally {
        setLoading(false);
      }
    };
    if (user_id) fetchLog();
  }, []);

  return (
    <div>
      <h1>評価履歴</h1>
      {loading && <p>読み込み中...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {logData.length > 0 && (
        <>
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={logData} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" tickFormatter={d => d} />
              <YAxis domain={[0, 5]} ticks={[1, 2, 3, 4, 5]} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="structure_score" name="構成" stroke="#1976d2" />
              <Line type="monotone" dataKey="speech_score" name="話速" stroke="#2e7d32" />
              <Line type="monotone" dataKey="knowledge_score" name="知識レベル" stroke="#fbc02d" />
              <Line type="monotone" dataKey="personas_score" name="ペルソナ" stroke="#d32f2f" />
              <Line type="monotone" dataKey="comparison_score" name="比較" stroke="#7b1fa2" />
            </LineChart>
          </ResponsiveContainer>
          <Typography variant="h6" align="center" sx={{ mt: 4, mb: 2 }}>総評履歴</Typography>
          <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            {logData.slice().reverse().map((item, idx) => (
              <Card key={idx} sx={{ mb: 2, maxWidth: 600, width: '100%' }}>
                <CardContent>
                  <Typography variant="caption" color="text.secondary" sx={{ float: 'left' }}>{item.date}</Typography>
                  <Typography variant="body1" sx={{ clear: 'both', mt: 2 }}>{item.summary}</Typography>
                </CardContent>
              </Card>
            ))}
          </Box>
        </>
      )}
      {logData.length === 0 && !loading && <p>データがありません</p>}
    </div>
  );
};

export default Log;