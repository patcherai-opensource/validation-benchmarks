import type { Metadata } from "next";
import "./globals.css";
import NavBar from "./components/NavBar"

export const metadata: Metadata = {
  title: "ManaPool",
  description: "Where Art Meets Investment",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
          <NavBar />
        {children}
      </body>
    </html>
  );
}
