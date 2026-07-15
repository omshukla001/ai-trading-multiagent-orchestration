import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Trading Agents | Multi-Agent Orchestration Dashboard",
  description: "Multi-agent AI trading system with real-time stock analysis, technical indicators, and intelligent decision-making",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="bg-gray-950 text-white antialiased">{children}</body>
    </html>
  );
}
