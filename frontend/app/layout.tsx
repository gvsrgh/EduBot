import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'EduBot - AI University Assistant',
  description: 'Chat with your university AI assistant',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
