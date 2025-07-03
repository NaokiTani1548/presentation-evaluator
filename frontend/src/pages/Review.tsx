import React, { useState } from 'react';
import { Stepper, Step, StepLabel, Button, Typography, Paper, Box, LinearProgress, Alert, Card, CardContent, Tabs, Tab, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';

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
  const [audioSample, setAudioSample] = useState<string | null>(null);
  const [slideModResult, setSlideModResult] = useState<any>(null);
  const [slideModText, setSlideModText] = useState<string | null>(null);

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
              // 新しいラベルの処理
              if (data.label === 'お手本音声サンプル（話速改善用）' && data.type === 'audio/wav-base64') {
                setAudioSample(data.result); // base64文字列を保存
                continue;
              }
              if (data.label === 'スライド修正案（構成改善用）' && data.type === 'slide_modification') {
                setSlideModResult(data.result?.image_base64 || null);
                setSlideModText(data.result?.text || null);
                continue;
              }
              // 通常のカードとして格納
              let parsed: any = data.result;
              if (typeof data.result === 'string') {
                try {
                  parsed = JSON.parse(data.result);
                } catch {
                  parsed = data.result;
                }
              }
              // ここでObject型はテキスト化して格納
              if (typeof parsed === 'object' && parsed !== null && !Array.isArray(parsed)) {
                // 知識レベルエージェントだけは従来通り
                if (data.label.includes('知識レベルエージェント')) {
                  cards.push({ label: data.label, result: JSON.stringify(parsed) });
                } else if (data.label.includes('総評エージェントの意見')) {
                  // 総評エージェントはオブジェクトのまま格納
                  cards.push({ label: data.label, result: parsed });
                } else {
                  // それ以外は値だけを連結してテキスト化
                  const values = Object.values(parsed).filter(v => typeof v === 'string');
                  cards.push({ label: data.label, result: values.join('\n') });
                }
              } else {
                cards.push({ label: data.label, result: parsed });
              }
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

  // 動画プレビュー用URL
  const videoUrl = videoFile ? URL.createObjectURL(videoFile) : '';

  // 総評だけ分離
  const summaryResult = results.find(r => r.label.includes('総評エージェントの意見'));
  const tabResults = results.filter(r => !r.label.includes('総評エージェントの意見') && r.label !== 'スライド修正案（構成改善用）');

  // レーダーチャート用データ生成
  let radarData: any[] = [];
  let summaryText = '';
  if (summaryResult) {
    let parsed: any = summaryResult.result;
    if (typeof parsed === 'string') {
      try {
        parsed = JSON.parse(parsed);
      } catch {
        // fallback: テキスト+スコア形式
        // テキスト末尾の5行がスコアである場合を考慮
        const lines = summaryResult.result.trim().split(/\r?\n/);
        const last5 = lines.slice(-5);
        const scores = last5.map(s => parseFloat(s)).filter(n => !isNaN(n));
        if (scores.length === 5) {
          radarData = [
            { item: '構成', score: scores[0] },
            { item: '話速', score: scores[1] },
            { item: '知識レベル', score: scores[2] },
            { item: 'ペルソナ', score: scores[3] },
            { item: '比較', score: scores[4] },
          ];
          summaryText = lines.slice(0, -5).join('\n');
        }
      }
    }
    if (typeof parsed === 'object' && parsed !== null && radarData.length === 0) {
      summaryText = parsed.summary || '';
      radarData = [
        { item: '構成', score: parsed.structure_score ?? 0 },
        { item: '話速', score: parsed.speech_score ?? 0 },
        { item: '知識レベル', score: parsed.knowledge_score ?? 0 },
        { item: 'ペルソナ', score: parsed.personas_score ?? 0 },
        { item: '比較', score: parsed.comparison_score ?? 0 },
      ];
    }
  }

  const user_id = localStorage.getItem('user_id');
  const user_name = localStorage.getItem('user_name');
  const email_address = localStorage.getItem('email_address');

  // PriorKnowledge用テーブル描画関数
  const renderPriorKnowledgeTable = (priorKnowledge: any) => {
    if (!priorKnowledge || !priorKnowledge.prerequisites || !Array.isArray(priorKnowledge.prerequisites)) return null;
    return (
      <TableContainer component={Paper} sx={{ my: 2 }}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>用語</TableCell>
              <TableCell>説明</TableCell>
              <TableCell>レベル</TableCell>
              <TableCell>説明の粒度</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {priorKnowledge.prerequisites.map((item: any, idx: number) => (
              <TableRow key={idx}>
                <TableCell>{item.term}</TableCell>
                <TableCell>{item.description}</TableCell>
                <TableCell>{item.level}</TableCell>
                <TableCell>{item.explained_level}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
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
          <Typography sx={{ mb: 2 }}>動画ファイル（mp4）とスライドファイル（pdf）をアップロードしてください</Typography>
          <label>
            <input
              type="file"
              accept="video/mp4"
              onChange={handleVideoChange}
              required
              style={{ display: 'none' }}
            />
            <Button variant="outlined" component="span">動画ファイル（.mp4）選択</Button>
            {videoFile && <span style={{ marginLeft: 8 }}>{videoFile.name}</span>}
          </label>
          <label style={{ marginLeft: 24 }}>
            <input
              type="file"
              accept="application/pdf"
              onChange={handlePdfChange}
              required
              style={{ display: 'none' }}
            />
            <Button variant="outlined" component="span">スライド（.pdf）選択</Button>
            {pdfFile && <span style={{ marginLeft: 8 }}>{pdfFile.name}</span>}
          </label>
          <Box sx={{ mt: 2 }}>
            <Button
              variant="contained"
              onClick={handleUpload}
              disabled={
                uploading ||
                !videoFile ||
                !pdfFile ||
                (videoFile && videoFile.type !== 'video/mp4') ||
                (pdfFile && pdfFile.type !== 'application/pdf')
              }
            >
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
          {videoUrl && (
            <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center' }}>
              <video src={videoUrl} controls style={{ width: 320, borderRadius: 8, marginBottom: 24 }} />
            </Box>
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
              <Box sx={{ ml: 2, flex: 1, display: 'flex', justifyContent: 'center' }}>
                <Card sx={{ minWidth: 250, maxWidth: 600 }}>
                  <CardContent>
                    <Typography variant="subtitle1" color="primary">{tabResults[tabIdx]?.label}</Typography>
                    {/* PriorKnowledge用テーブル表示 */}
                    {tabResults[tabIdx]?.label.includes('知識レベルエージェント') && (() => {
                      let parsed: any = tabResults[tabIdx]?.result;
                      if (typeof parsed === 'string') {
                        try { parsed = JSON.parse(parsed); } catch { parsed = null; }
                      }
                      if (parsed && typeof parsed === 'object' && parsed.prerequisites && Array.isArray(parsed.prerequisites)) {
                        return (
                          <>
                            <Typography variant="body2" style={{ whiteSpace: 'pre-line', marginBottom: 8 }}>{parsed.summary}</Typography>
                            {renderPriorKnowledgeTable(parsed)}
                          </>
                        );
                      } else {
                        return <Typography variant="body2" style={{ whiteSpace: 'pre-line' }} >{tabResults[tabIdx]?.result}</Typography>;
                      }
                    })()}
                    {/* 通常のテキスト表示 */}
                    {!tabResults[tabIdx]?.label.includes('知識レベルエージェント') && (
                      <Typography variant="body2" style={{ whiteSpace: 'pre-line' }} >{tabResults[tabIdx]?.result}</Typography>
                    )}
                  </CardContent>
                </Card>
              </Box>
            </Box>
          )}
          {summaryResult && (
            <Box sx={{ mt: 4, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <Card sx={{ minWidth: 300, maxWidth: 700, border: '2px solid #1976d2', background: '#f5faff', p: 2 }}>
                <CardContent>
                  <Typography variant="h6" color="primary" align="center">総評エージェントの意見</Typography>
                  <Box sx={{ width: 350, height: 300, mx: 'auto' }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
                        <PolarGrid />
                        <PolarAngleAxis dataKey="item" />
                        <PolarRadiusAxis angle={30} domain={[0, 5]} />
                        <Radar name="評価" dataKey="score" stroke="#1976d2" fill="#1976d2" fillOpacity={0.4} />
                      </RadarChart>
                    </ResponsiveContainer>
                  </Box>
                  <Typography variant="body1" style={{ whiteSpace: 'pre-line' }} align="center">{summaryText}</Typography>
                  {/* お手本音声サンプルがあれば再生UIを表示 */}
                  {audioSample && (
                    <Box sx={{ mt: 3, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                      <Typography variant="subtitle2" color="primary" align="center">お手本音声サンプル（話速改善用）</Typography>
                      <audio controls style={{ marginTop: 8 }}>
                        <source src={`data:audio/wav;base64,${audioSample}`} type="audio/wav" />
                        お使いのブラウザは audio タグをサポートしていません。
                      </audio>
                    </Box>
                  )}
                  {/* スライド修正案があればテキストと画像を表示 */}
                  {slideModResult && (
                    <Box sx={{ mt: 3, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                      <Typography variant="subtitle2" color="primary" align="center">スライド修正案（構成改善用）</Typography>
                      {slideModText && (
                        <Typography variant="body2" style={{ whiteSpace: 'pre-line', marginBottom: 8 }} align="center">{slideModText}</Typography>
                      )}
                      <img src={`data:image/png;base64,${slideModResult}`} alt="slide modification" style={{ marginTop: 8, maxWidth: 500, borderRadius: 8, border: '1px solid #ccc' }} />
                    </Box>
                  )}
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