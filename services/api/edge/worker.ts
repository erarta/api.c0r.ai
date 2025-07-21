import { Hono } from 'hono';
import { v4 as uuidv4 } from 'uuid';
import { handleR2Upload, getSignedUrl } from './lib/r2';
import { analyzePhotoWithOpenAI } from './lib/openai';
import { decrementCreditsAndLog } from './lib/supabase';

const app = new Hono();

app.post('/v1/analyze', async (c) => {
  try {
    const body = await c.req.parseBody();
    const photo = body['photo'];
    const userId = body['user_id'];
    if (!photo || !userId) {
      return c.json({ error: 'Missing photo or user_id' }, 400);
    }
    // Ensure photo is a File object
    if (typeof photo === 'string' || !(photo instanceof File)) {
      return c.json({ error: 'Photo must be a File upload (multipart/form-data)' }, 400);
    }
    // Ensure userId is a string
    const userIdStr = typeof userId === 'string' ? userId : String(userId);
    // Save photo to R2
    const photoId = uuidv4();
    const r2Url = await handleR2Upload(photo, photoId);
    // Generate signed URL for OpenAI
    const signedUrl = await getSignedUrl(photoId);
    // Call OpenAI Vision
    const kbzhu = await analyzePhotoWithOpenAI(signedUrl);
    // Update Supabase: decrement credits, add log
    await decrementCreditsAndLog(userIdStr, photoId, kbzhu);
    // Return result
    return c.json({ kbzhu });
  } catch (err: any) {
    console.error('Error in /v1/analyze:', err);
    return c.json({ error: 'Analysis failed' }, 500);
  }
});

export default app; 