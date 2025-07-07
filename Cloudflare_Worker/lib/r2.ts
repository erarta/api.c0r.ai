// Save photo to R2 bucket with UUID
export async function handleR2Upload(photo: File, photoId: string): Promise<string> {
  // @ts-ignore: R2 binding is available in Worker environment
  const r2 = (globalThis as any).R2_BUCKET;
  if (!r2) throw new Error('R2_BUCKET binding not found');
  await r2.put(photoId, await photo.arrayBuffer());
  return `r2://${photoId}`;
}

// Generate signed URL for R2 object
export async function getSignedUrl(photoId: string): Promise<string> {
  // @ts-ignore: R2 binding is available in Worker environment
  const r2 = (globalThis as any).R2_BUCKET;
  if (!r2) throw new Error('R2_BUCKET binding not found');
  // Use NEUCOR_DOMAIN from env
  const domain = (globalThis as any).NEUCOR_DOMAIN || 'neucor.ai';
  return `https://r2-public.${domain}/${photoId}`;
} 