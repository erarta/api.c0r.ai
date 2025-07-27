// Use globalThis for Worker environment variable compatibility
export async function analyzePhotoWithOpenAI(signedUrl: string): Promise<{calories: number, protein: number, fats: number, carbs: number}> {
  // @ts-ignore: OPENAI_API_KEY binding is available in Worker environment
  const apiKey = (globalThis as any).OPENAI_API_KEY;
  if (!apiKey) throw new Error('OPENAI_API_KEY not set');

  const res = await fetch('https://api.openai.com/v1/vision/analyze', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ image_url: signedUrl })
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`OpenAI API error: ${res.status} ${text}`);
  }

  const data = await res.json();
  // Assume OpenAI returns { kbzhu: { calories, protein, fats, carbs } }
  if (!data.kbzhu) throw new Error('No KBZHU in OpenAI response');
  return data.kbzhu;
} 