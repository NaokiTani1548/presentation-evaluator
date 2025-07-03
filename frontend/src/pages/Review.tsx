import React, { useState } from 'react';
import { Stepper, Step, StepLabel, Button, Typography, Paper, Box, LinearProgress, Alert, Card, CardContent, Tabs, Tab } from '@mui/material';

const steps = ['アップロード', '評価中', '完了'];

interface ResultCard {
  label: string;
  result: string;
}

const StepperSample: React.FC = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<ResultCard[]>([]);
  const [tabIdx, setTabIdx] = useState(0);

  const handleVideoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) setVideoFile(e.target.files[0]);
  };
  const handlePdfChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) setPdfFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    setError(null);
    setResults([]);
    setTabIdx(0);
    if (!videoFile || !pdfFile) {
      setError('動画ファイルとPDFファイルの両方を選択してください');
      return;
    }
    setUploading(true);
    setActiveStep(1); // 評価中へ
    try {
      const formData = new FormData();
      formData.append('slide', pdfFile); // slide
      formData.append('audio', videoFile); // audio
      formData.append('user_id', '0');
      const response = await fetch('http://127.0.0.1:8000/evaluate/', {
        method: 'POST',
        body: formData,
      });
      if (response.body) {
        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let buffer = '';
        let cards: ResultCard[] = [];
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          let lines = buffer.split('\n');
          buffer = lines.pop() || '';
          for (const line of lines) {
            if (line.trim()) {
              const data = JSON.parse(line);
              // resultがJSON文字列ならパースして値を連結
              let parsed: any = data.result;
              if (typeof data.result === 'string') {
                try {
                  parsed = JSON.parse(data.result);
                } catch {
                  parsed = data.result;
                }
              }
              let text = '';
              if (typeof parsed === 'object' && parsed !== null) {
                text = Object.values(parsed).map(String).join('\n');
              } else {
                text = String(parsed);
              }
              cards.push({ label: data.label, result: text });
            }
          }
          setResults([...cards]);
        }
      }
      setActiveStep(2); // 完了へ
    } catch (e) {
      setError('アップロードまたは評価に失敗しました');
    } finally {
      setUploading(false);
    }
  };

  const handleReset = () => {
    setActiveStep(0);
    setVideoFile(null);
    setPdfFile(null);
    setError(null);
    setResults([]);
    setTabIdx(0);
  };

  // 総評だけ分離
  const summaryResult = results.find(r => r.label.includes('総評エージェントの意見'));
  const tabResults = results.filter(r => !r.label.includes('総評エージェントの意見'));

  return (
    <Paper elevation={2} sx={{ p: 4, borderRadius: 3 }}>
      <Typography variant="h5" mb={2} color="primary">Review Meeting</Typography>
      <Stepper activeStep={activeStep} sx={{ mb: 2 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>
      {activeStep === 0 && (
        <Box>
          <Typography sx={{ mb: 2 }}>動画ファイルとPDFファイルをアップロードしてください</Typography>
          <input type="file" accept="video/*" onChange={handleVideoChange} />
          <input type="file" accept="application/pdf" onChange={handlePdfChange} style={{ marginLeft: 16 }} />
          <Box sx={{ mt: 2 }}>
            <Button variant="contained" onClick={handleUpload} disabled={uploading || !videoFile || !pdfFile}>
              アップロード
            </Button>
          </Box>
          {uploading && <LinearProgress sx={{ mt: 2 }} />}
          {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
        </Box>
      )}
      {(activeStep === 1 || activeStep === 2) && (
        <Box>
          {activeStep === 1 && (
            <>
              <Typography sx={{ mb: 2 }}>評価中です。しばらくお待ちください...</Typography>
              <LinearProgress />
            </>
          )}
          {tabResults.length > 0 && (
            <Box sx={{ mt: 2, display: 'flex' }}>
              <Tabs
                orientation="vertical"
                value={tabIdx}
                onChange={(_, v) => setTabIdx(v)}
                variant="scrollable"
                scrollButtons="auto"
                sx={{ borderRight: 1, borderColor: 'divider', minWidth: 180 }}
              >
                {tabResults.map((res, idx) => (
                  <Tab key={idx} label={res.label} />
                ))}
              </Tabs>
              <Box sx={{ ml: 2, flex: 1 }}>
                <Card sx={{ minWidth: 250, maxWidth: 600 }}>
                  <CardContent>
                    <Typography variant="subtitle1" color="primary">{tabResults[tabIdx]?.label}</Typography>
                    <Typography variant="body2" style={{ whiteSpace: 'pre-line' }}>{tabResults[tabIdx]?.result}</Typography>
                  </CardContent>
                </Card>
              </Box>
            </Box>
          )}
          {summaryResult && (
            <Box sx={{ mt: 4 }}>
              <Card sx={{ minWidth: 300, maxWidth: 700, border: '2px solid #1976d2', background: '#f5faff' }}>
                <CardContent>
                  <Typography variant="h6" color="primary">{summaryResult.label}</Typography>
                  <Typography variant="body1" style={{ whiteSpace: 'pre-line' }}>{summaryResult.result}</Typography>
                </CardContent>
              </Card>
            </Box>
          )}
          {activeStep === 2 && (
            <Button onClick={handleReset} sx={{ mt: 2 }}>リセット</Button>
          )}
        </Box>
      )}
    </Paper>
  );
};
export default StepperSample;