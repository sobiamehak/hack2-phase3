import './globals.css';
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { AuthProvider } from '../contexts/AuthContext';
import ChatbotWidget from '../components/ChatbotWidget';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Todo App',
  description: 'A secure, multi-user todo application',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.className} min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100`}>
        <AuthProvider>
          <div className="min-h-screen">
            {children}
            <ChatbotWidget />
          </div>
        </AuthProvider>
      </body>
    </html>
  );
}