type KBZHU = { calories: number, protein: number, fats: number, carbs: number };

export async function decrementCreditsAndLog(userId: string, photoId: string, kbzhu: KBZHU): Promise<void> {
  // @ts-ignore: Supabase env bindings for Worker
  const supabaseUrl = (globalThis as any).SUPABASE_URL;
  const supabaseKey = (globalThis as any).SUPABASE_SERVICE_KEY;
  if (!supabaseUrl || !supabaseKey) throw new Error('Supabase env vars not set');

  // Decrement credits
  const updateRes = await fetch(`${supabaseUrl}/rest/v1/users?telegram_id=eq.${userId}`, {
    method: 'PATCH',
    headers: {
      'apikey': supabaseKey,
      'Authorization': `Bearer ${supabaseKey}`,
      'Content-Type': 'application/json',
      'Prefer': 'return=representation',
    },
    body: JSON.stringify({ credits_remaining: { decrement: 1 } }),
  });
  if (!updateRes.ok) {
    const text = await updateRes.text();
    throw new Error(`Supabase update error: ${updateRes.status} ${text}`);
  }

  // Add log entry
  const logRes = await fetch(`${supabaseUrl}/rest/v1/logs`, {
    method: 'POST',
    headers: {
      'apikey': supabaseKey,
      'Authorization': `Bearer ${supabaseKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      user_id: userId,
      photo_url: photoId,
      kbzhu,
      timestamp: new Date().toISOString(),
      model_used: 'openai-vision',
    }),
  });
  if (!logRes.ok) {
    const text = await logRes.text();
    throw new Error(`Supabase log error: ${logRes.status} ${text}`);
  }
} 