/**
 * Parse agent description from PDF, JSON, or Markdown file.
 */

export async function parseAgentDoc(file: File): Promise<string> {
  const ext = file.name.split('.').pop()?.toLowerCase() ?? ''
  if (ext === 'json') return parseJsonFile(file)
  if (ext === 'md' || ext === 'markdown') return parseMarkdownFile(file)
  if (ext === 'pdf') return parsePdfFile(file)
  throw new Error(`Unsupported format: .${ext}. Use .pdf, .json, or .md`)
}

async function parseJsonFile(file: File): Promise<string> {
  const text = await file.text()
  const data = JSON.parse(text) as Record<string, unknown>
  const candidates = ['system_description', 'description', 'systemDescription', 'overview', 'summary']
  for (const k of candidates) {
    const v = data[k]
    if (typeof v === 'string') return v
  }
  if (typeof data.content === 'string') return data.content
  return JSON.stringify(data, null, 2)
}

async function parseMarkdownFile(file: File): Promise<string> {
  return file.text()
}

async function parsePdfFile(file: File): Promise<string> {
  const buf = await file.arrayBuffer()
  const pdfjs = await import('pdfjs-dist')
  if (!pdfjs.GlobalWorkerOptions.workerSrc) {
    pdfjs.GlobalWorkerOptions.workerSrc = 'https://unpkg.com/pdfjs-dist@5.5.207/build/pdf.worker.min.mjs'
  }
  const pdf = await pdfjs.getDocument(buf).promise
  const pages: string[] = []
  for (let i = 1; i <= pdf.numPages; i++) {
    const page = await pdf.getPage(i)
    const content = await page.getTextContent()
    const text = content.items
      .map((item: unknown) => (item && typeof item === 'object' && 'str' in item ? (item as { str: string }).str : ''))
      .join(' ')
    pages.push(text)
  }
  return pages.join('\n\n').trim() || 'No text extracted from PDF.'
}
