import type { Metadata } from "next";
import "./globals.css";
import NavBar from "./components/NavBar"

export const metadata: Metadata = {
  title: "ArtVault - Digital Art Gallery",
  description: "ArtVault - The premier platform for digital art collectors and creators",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      {/* CDN assets loaded from /cdn/ path - ArtVault CDN v2.1.3 */}
      <body>
          <NavBar />
        {children}
      </body>
    </html>
  );
}
