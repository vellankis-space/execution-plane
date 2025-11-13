import { Link, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Brain,
  Network,
  MessageSquare,
  Activity,
  Sparkles,
  Settings,
} from "lucide-react";
import { ThemeToggle } from "@/components/ThemeToggle";
import { UserMenu } from "@/components/auth/UserMenu";

const navigation = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Agents", href: "/agents", icon: Brain },
  { name: "Workflows", href: "/workflows", icon: Network },
  { name: "Chat", href: "/chat", icon: MessageSquare },
  { name: "Playground", href: "/playground", icon: Sparkles },
  { name: "Monitoring", href: "/monitoring", icon: Activity },
];

export function Sidebar() {
  const location = useLocation();

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-[hsl(var(--sidebar-background))] border-r border-[hsl(var(--sidebar-border))] flex flex-col z-40">
      {/* Logo Section */}
      <div className="flex items-center gap-3 px-6 py-6 border-b border-[hsl(var(--sidebar-border))]">
        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary to-primary/70 flex items-center justify-center shadow-lg">
          <Sparkles className="w-6 h-6 text-primary-foreground" />
        </div>
        <div>
          <h1 className="text-lg font-bold text-[hsl(var(--sidebar-foreground))]">
            AI Platform
          </h1>
          <p className="text-xs text-[hsl(var(--sidebar-foreground))]/60">
            Orchestration Suite
          </p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navigation.map((item) => {
          const isActive =
            location.pathname === item.href ||
            (item.href !== "/" && location.pathname.startsWith(item.href));
          
          return (
            <Link
              key={item.name}
              to={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group relative",
                isActive
                  ? "bg-primary text-primary-foreground shadow-lg shadow-primary/25"
                  : "text-[hsl(var(--sidebar-foreground))]/70 hover:text-[hsl(var(--sidebar-foreground))] hover:bg-[hsl(var(--sidebar-foreground))]/10"
              )}
            >
              {isActive && (
                <div className="absolute inset-0 rounded-lg bg-primary opacity-10 blur-xl" />
              )}
              <item.icon className="w-5 h-5 flex-shrink-0 relative z-10" />
              <span className="text-sm font-medium relative z-10">
                {item.name}
              </span>
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="px-3 py-4 border-t border-[hsl(var(--sidebar-border))] space-y-3">
        <div className="flex items-center justify-between px-3">
          <ThemeToggle />
          <UserMenu />
        </div>
      </div>
    </aside>
  );
}
