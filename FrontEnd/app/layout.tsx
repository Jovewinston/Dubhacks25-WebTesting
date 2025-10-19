import type { Metadata } from 'next'
import { Geist, Geist_Mono } from 'next/font/google'
import { Analytics } from '@vercel/analytics/next'
import './globals.css'

const geist = Geist({ subsets: ["latin"] });
const geistMono = Geist_Mono({ subsets: ["latin"] });

/**
 * Root layout metadata for the WebVoyant application
 */
export const metadata: Metadata = {
  title: 'WebVoyant - The Future of Web Testing',
  description: 'Automate your web testing with AI-powered precision. Test across multiple browsers and devices with ease.',
  generator: 'WebVoyant',
}

/**
 * Root layout component for the WebVoyant application
 */
export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className={`font-sans antialiased`} suppressHydrationWarning={true}>
        {children}
        <Analytics />
      </body>
    </html>
  )
}
