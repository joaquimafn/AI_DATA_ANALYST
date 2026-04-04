import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'AI Data Analyst',
  description: 'Converta perguntas em linguagem natural para SQL e obtenha insights automaticamente',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt-BR">
      <body className="antialiased">{children}</body>
    </html>
  )
}
