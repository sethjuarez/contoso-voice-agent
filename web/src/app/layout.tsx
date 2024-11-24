import './globals.css'
import Footer from '@/components/footer';
import Header from '@/components/header';
import type { Metadata } from "next";
import { version } from '@/store/version';
import styles from './layout.module.css';



export const metadata: Metadata = {
  title: "Contoso Outdoors",
  description:
    "Embrace Adventure with Contoso Outdoors - Your Ultimate Partner in Exploring the Unseen!",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <Header />
        {children}
        <Footer />
        <div className={styles.version}>{version}</div>
      </body>
    </html>
  );
}
