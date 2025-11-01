export const metadata = {
  title: "AI Chat",
  description: "Business-ready chat UI powered by FastAPI backend"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  );
}


