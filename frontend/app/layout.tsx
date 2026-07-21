import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Providers from "@/components/Providers";
import Sidebar from "@/components/Sidebar";
import NetworkMonitor from "@/components/NetworkMonitor";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "ATS Resume Analyzer",
  description: "Offline AI-powered ATS resume matching and feedback",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-zinc-950 text-zinc-100 min-h-screen flex relative`}>
        <Providers>
          <Sidebar />
          {/* Main Content */}
          <main className="flex-1 flex flex-col p-8 overflow-y-auto relative z-0">
            <NetworkMonitor>
              {children}
            </NetworkMonitor>
          </main>
        </Providers>
      </body>
    </html>
  );
}
