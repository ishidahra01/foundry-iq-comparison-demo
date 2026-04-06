import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Foundry IQ Comparison Demo",
  description: "Compare Classic RAG vs Foundry IQ Agentic Retrieval",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
