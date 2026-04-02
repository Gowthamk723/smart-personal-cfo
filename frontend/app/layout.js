import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/lib/AuthContext";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

export const metadata = {
  title: "Smart Personal CFO",
  description: "AI-Powered Financial Advisor",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      {/* Added the font variable to the body class */}
      <body className={`${geistSans.variable} antialiased`}>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}