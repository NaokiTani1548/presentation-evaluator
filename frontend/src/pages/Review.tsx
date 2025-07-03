import React, { useState } from 'react';
import { Stepper, Step, StepLabel, Button, Typography, Paper, Box, LinearProgress, Alert, Card, CardContent } from '@mui/material';

const steps = ['アップロード', '評価中', '完了'];

const StepperSample: React.FC = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<{ label: string; result: string }[]>([]);

  const handleVideoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) setVideoFile(e.target.files[0]);
  };
  const handlePdfChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) setPdfFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    setError(null);
    setResults([]);
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
      const response = await fetch('http://127.0.0.1:8000/evaluate/', {
        method: 'POST',
        body: formData,
      });
      if (response.body) {
        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let buffer = '';
        let cards: { label: string; result: string }[] = [];
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          let lines = buffer.split('\n');
          buffer = lines.pop() || '';
          for (const line of lines) {
            if (line.trim()) {
              const data = JSON.parse(line);
              cards.push(data);
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
  };

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
      {activeStep === 1 && (
        <Box>
          <Typography sx={{ mb: 2 }}>評価中です。しばらくお待ちください...</Typography>
          <LinearProgress />
          <Box sx={{ mt: 2, display: 'flex', flexWrap: 'wrap', gap: 2 }}>
            {results.map((res, idx) => (
              <Card key={idx} sx={{ minWidth: 250, maxWidth: 400 }}>
                <CardContent>
                  <Typography variant="subtitle1" color="primary">{res.label}</Typography>
                  {(() => {
                    let parsed: any = res.result;
                    if (typeof res.result === 'string') {
                      try {
                        parsed = JSON.parse(res.result);
                      } catch {
                        parsed = res.result;
                      }
                    }
                    if (typeof parsed === 'object' && parsed !== null) {
                      return Object.values(parsed).map((val, i) => (
                        <Typography variant="body2" key={i} paragraph>{String(val)}</Typography>
                      ));
                    } else {
                      return <Typography variant="body2">{String(parsed)}</Typography>;
                    }
                  })()}
                </CardContent>
              </Card>
            ))}
          </Box>
        </Box>
      )}
      {activeStep === 2 && (
        <Box>
          <Typography>すべて完了しました！</Typography>
          <Box sx={{ mt: 2, display: 'flex', flexWrap: 'wrap', gap: 2 }}>
            {results.map((res, idx) => (
              <Card key={idx} sx={{ minWidth: 250, maxWidth: 400 }}>
                <CardContent>
                  <Typography variant="subtitle1" color="primary">{res.label}</Typography>
                  {(() => {
                    let parsed: any = res.result;
                    if (typeof res.result === 'string') {
                      try {
                        parsed = JSON.parse(res.result);
                      } catch {
                        parsed = res.result;
                      }
                    }
                    if (typeof parsed === 'object' && parsed !== null) {
                      return Object.values(parsed).map((val, i) => (
                        <Typography variant="body2" key={i} paragraph>
                          {String(val)}
                        </Typography>
                      ));
                    } else {
                      return <Typography variant="body2">{String(parsed)}</Typography>;
                    }
                  })()}
                </CardContent>
              </Card>
            ))}
          </Box>
          <Button onClick={handleReset} sx={{ mt: 2 }}>リセット</Button>
        </Box>
      )}
    </Paper>
  );
};
export default StepperSample;