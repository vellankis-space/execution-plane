import { ReactNode } from "react";
import { Sidebar } from "./Sidebar";

interface MainLayoutProps {
  children: ReactNode;
}

export function MainLayout({ children }: MainLayoutProps) {
  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <main className="flex-1 ml-64 overflow-y-auto bg-background">
        <div className="min-h-screen">
          {children}
        </div>
      </main>
    </div>
  );
}
