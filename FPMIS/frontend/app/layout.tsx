import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'FPMIS - Forensic Post-Mortem Intelligence System',
  description: 'A unified digital platform for forensic post-mortem intelligence',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="font-sans">{children}</body>
    </html>
  );
}
