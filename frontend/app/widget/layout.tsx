import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "EduBot+ Widget",
  robots: "noindex, nofollow",
};

export default function WidgetLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
