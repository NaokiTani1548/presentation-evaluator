// mockEvaluationResponse.ts
export const mockEvaluationStream = [
  {
    label: '話速エージェントの意見',
    result: JSON.stringify({
      speech_rate_review: '話速がやや早めです。もう少しゆっくり話すと良いでしょう。',
      speaking_style_review: '落ち着いたトーンで話せていました。'
    })
  },
  {
    label: '知識レベルエージェントの意見',
    result: JSON.stringify({
      summary: '前提知識がやや専門的です。',
      prerequisites: [
        {
          term: 'ニューラルネットワーク',
          description: '機械学習で用いられる数学モデル',
          level: '中級',
          explained_level: '簡単な例を用いた説明'
        }
      ]
    })
  },
  {
    label: '比較AIの意見',
    result: JSON.stringify({
      comparison_evaluation: '前回よりも改善が見られます。'
    })
  },
  {
    label: '総評エージェントの意見',
    result: JSON.stringify({
      structure_score: 4,
      speech_score: 3,
      knowledge_score: 4,
      personas_score: 5,
      comparison_score: 4,
      summary: '全体的に良いプレゼンでした。特に構成とペルソナへの配慮が優れていました。'
    })
  }
];
