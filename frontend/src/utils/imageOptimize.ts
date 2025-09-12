export async function optimizeImage(
  file: File,
  maxSide = 1400,
  quality = 0.85
): Promise<File> {
  if (!file.type.startsWith('image/')) return file
  const bmp = await createImageBitmap(file)
  const { width, height } = bmp
  const scale = Math.min(1, maxSide / Math.max(width, height))
  if (scale >= 1) return file
  const canvas = document.createElement('canvas')
  canvas.width = Math.round(width * scale)
  canvas.height = Math.round(height * scale)
  const ctx = canvas.getContext('2d')!
  ctx.drawImage(bmp, 0, 0, canvas.width, canvas.height)
  const blob: Blob = await new Promise(res => canvas.toBlob(b => res(b!), 'image/jpeg', quality))
  return new File([blob], file.name.replace(/\.(png|jpe?g)$/i,'') + '_opt.jpg', { type: 'image/jpeg' })
}