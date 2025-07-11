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
  const [radarData, setRadarData] = useState<any[]>([]);
  const [summaryText, setSummaryText] = useState('');
  const user_id = localStorage.getItem('user_id');
  const user_name = localStorage.getItem('user_name');
  const email_address = localStorage.getItem('email_address');

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
    setUploading(true); //アップロード中
    setActiveStep(1); // 評価中へ
    try {
      const formData = new FormData();
      formData.append('slide', pdfFile);
      formData.append('audio', videoFile);
      formData.append('user_id', user_id ?? '100');
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
          if (done) {
            console.log("📦 ストリーム終了");
            break;
          }
          const chunk = decoder.decode(value, { stream: true });
          console.log("📥 chunk 受信:", chunk);
          buffer += chunk;

          let lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.trim()) {
              let data;
              try {
                data = JSON.parse(line);
                console.log("✅ パース成功:", data);
              } catch (err) {
                console.error("❌ JSON パース失敗:", err, line);
                continue;
              }

              // 1. お手本音声サンプル（話速改善用）
              if (data.label === 'お手本音声サンプル（話速改善用）' && data.type === 'audio/wav-base64') {
                console.log("🎵 音声サンプル取得:", data.result);
                setAudioSample(data.result);
                continue;
              }

              // 2. スライド修正案（構成改善用）
              if (data.label === 'スライド修正案（構成改善用）' && data.type === 'slide_modification') {
                console.log("🖼 スライド修正案取得:", data.result?.text || null);
                setSlideModResult(data.result?.image_base64 || null);
                setSlideModText(data.result?.text || null);
                continue;
              }

              // 3. 構成エージェントの意見
              if (data.label === '構成エージェントの意見') {
                let parsed = data.result;
                if (typeof parsed === 'string') {
                  try { parsed = JSON.parse(parsed); } catch { /* ignore */ }
                }
                console.log("構成エージェント:", parsed.review ?? JSON.stringify(parsed))
                cards.push({ label: data.label, result: parsed.review ?? JSON.stringify(parsed) });
                continue;
              }

              // 4. 話速エージェントの意見
              if (data.label === '話速エージェントの意見') {
                let parsed = data.result;
                if (typeof parsed === 'string') {
                  try { parsed = JSON.parse(parsed); } catch { /* ignore */ }
                }
                const values = [parsed.speech_rate_review, parsed.speaking_style_review].filter(Boolean);
                console.log("話速エージェント:", values);
                cards.push({ label: data.label, result: values.length ? values.join('\n') : JSON.stringify(parsed) });
                continue;
              }

              // 5. 知識レベルエージェントの意見
              if (data.label.includes('知識レベルエージェント')) {
                let parsed = data.result;
                if (typeof parsed === 'string') {
                  try { parsed = JSON.parse(parsed); } catch { /* ignore */ }
                }
                console.log("知識レベルエージェント:", parsed);
                cards.push({ label: data.label, result: JSON.stringify(parsed) });
                continue;
              }

              // 7. 比較AIの意見
              if (data.label === '比較AIの意見') {
                let parsed = data.result;
                if (typeof parsed === 'string') {
                  try { parsed = JSON.parse(parsed); } catch { /* ignore */ }
                }
                console.log("比較AIの意見:", parsed.comparison_evaluation ?? JSON.stringify(parsed));
                cards.push({ label: data.label, result: parsed.comparison_evaluation ?? JSON.stringify(parsed) });
                continue;
              }

              // 8. 総評エージェントの意見
              if (data.label.includes('総評エージェントの意見')) {
                let parsed = data.result;
                let scores: number[] = [];
                let summary = '';
                if (typeof parsed === 'string') {
                  try { parsed = JSON.parse(parsed); } catch { /* ignore */ }
                }
                if (typeof parsed === 'object' && parsed !== null) {
                  scores = [
                    parsed.structure_score,
                    parsed.speech_score,
                    parsed.knowledge_score,
                    parsed.personas_score,
                    parsed.comparison_score,
                  ].map(s => typeof s === 'number' ? s : 0);
                  summary = parsed.summary || '';
                }
                if (scores.length === 5) {
                  setRadarData([
                    { item: '構成', score: scores[0] },
                    { item: '話速', score: scores[1] },
                    { item: '知識レベル', score: scores[2] },
                    { item: 'ペルソナ', score: scores[3] },
                    { item: '比較', score: scores[4] },
                  ]);
                  setSummaryText(summary);
                }
                continue;
              }

               // 6. ペルソナ別エージェントの意見
              if (data.label.includes('エージェントの意見')) {
                let parsed = data.result;
                if (typeof parsed === 'string') {
                  try { parsed = JSON.parse(parsed); } catch { /* ignore */ }
                }
                console.log("ペルソナ別エージェントの意見:", parsed);
                cards.push({ label: data.label, result: parsed });
                continue;
              }

              // 9. その他（上記以外）
              let parsed = data.result;
              if (typeof parsed === 'string') {
                try { parsed = JSON.parse(parsed); } catch { /* ignore */ }
              }
              if (typeof parsed === 'object' && parsed !== null && !Array.isArray(parsed)) {
                const values = Object.values(parsed).filter(v => typeof v === 'string');
                cards.push({ label: data.label, result: values.join('\n') });
              } else {
                cards.push({ label: data.label, result: parsed });
              }
            }else {
              continue;
            }
          }
        }
        setResults([...cards]);
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
              <Typography sx={{ mb: 2 }}>! リロードしないでください</Typography>
              <LinearProgress />
            </>
          )}
          {videoUrl && (
            <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center' }}>
              <video src={videoUrl} controls style={{ width: 320, borderRadius: 8, marginBottom: 24 }} />
            </Box>
          )}
          {results.length > 0 && (
            <Box sx={{ mt: 2, display: 'flex' }}>
              <Tabs
                orientation="vertical"
                value={tabIdx}
                onChange={(_, v) => setTabIdx(v)}
                variant="scrollable"
                scrollButtons="auto"
                sx={{ borderRight: 1, borderColor: 'divider', minWidth: 180 }}
              >
                {results.map((res, idx) => (
                  <Tab key={idx} label={res.label} />
                ))}
              </Tabs>
              <Box sx={{ ml: 2, flex: 1, display: 'flex', justifyContent: 'center' }}>
                <Card sx={{ minWidth: 250, maxWidth: 600 }}>
                  <CardContent>
                    <Typography variant="subtitle1" color="primary">{results[tabIdx]?.label}</Typography>
                    {/* PriorKnowledge用テーブル表示 */}
                    {results[tabIdx]?.label.includes('知識レベルエージェント') && (() => {
                      let parsed: any = results[tabIdx]?.result;
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
                        return <Typography variant="body2" style={{ whiteSpace: 'pre-line' }} >{results[tabIdx]?.result}</Typography>;
                      }
                    })()}
                    {/* 通常のテキスト表示 */}
                    {!results[tabIdx]?.label.includes('知識レベルエージェント') && (
                      <Typography variant="body2" style={{ whiteSpace: 'pre-line' }} >{results[tabIdx]?.result}</Typography>
                    )}
                  </CardContent>
                </Card>
              </Box>
            </Box>
          )}
          {summaryText != '' && (
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