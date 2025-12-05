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
  Server,
  Eye,
} from "lucide-react";
import { ThemeToggle } from "@/components/ThemeToggle";
import { UserMenu } from "@/components/auth/UserMenu";

const navigation = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Agents", href: "/agents", icon: Brain },
  { name: "Workflows", href: "/workflows", icon: Network },
  { name: "MCP Catalog", href: "/mcp-servers", icon: Server },
  { name: "Chat", href: "/chat", icon: MessageSquare },
  { name: "Playground", href: "/playground", icon: Sparkles },
  { name: "Monitoring", href: "/monitoring", icon: Activity },
  { name: "Observability", href: "/observability", icon: Eye },
];

interface SidebarProps {
  isCollapsed?: boolean;
}

export function Sidebar({ isCollapsed = false, onMouseEnter, onMouseLeave }: SidebarProps & { onMouseEnter?: () => void, onMouseLeave?: () => void }) {
  const location = useLocation();

  return (
    <aside
      className={cn(
        "fixed left-0 top-0 h-screen bg-[hsl(var(--sidebar-background))] border-r border-[hsl(var(--sidebar-border))] flex flex-col z-40 transition-all duration-300 ease-[cubic-bezier(0.4,0,0.2,1)]",
        isCollapsed ? "w-20" : "w-64"
      )}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
    >
      {/* Logo Section */}
      <div className={cn(
        "flex items-center gap-3 px-6 py-6 border-b border-[hsl(var(--sidebar-border))] transition-all duration-300",
        isCollapsed ? "justify-center px-2" : ""
      )}>
        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary to-primary/70 flex items-center justify-center shadow-lg flex-shrink-0">
          <Sparkles className="w-6 h-6 text-primary-foreground" />
        </div>
        <div className={cn("overflow-hidden transition-all duration-300", isCollapsed ? "w-0 opacity-0" : "w-auto opacity-100")}>
          <h1 className="text-lg font-bold text-[hsl(var(--sidebar-foreground))] whitespace-nowrap">
            Intelligentic AI
          </h1>
          <p className="text-xs text-[hsl(var(--sidebar-foreground))]/60 whitespace-nowrap">
            Agent & Workflow Management
          </p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto overflow-x-hidden">
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
                  : "text-[hsl(var(--sidebar-foreground))]/70 hover:text-[hsl(var(--sidebar-foreground))] hover:bg-[hsl(var(--sidebar-foreground))]/10",
                isCollapsed ? "justify-center" : ""
              )}
            >
              {isActive && (
                <div className="absolute inset-0 rounded-lg bg-primary opacity-10 blur-xl" />
              )}
              <item.icon className="w-5 h-5 flex-shrink-0 relative z-10" />
              <span className={cn(
                "text-sm font-medium relative z-10 transition-all duration-300",
                isCollapsed ? "w-0 opacity-0 hidden" : "w-auto opacity-100"
              )}>
                {item.name}
              </span>

              {/* Tooltip for mini mode */}
              {isCollapsed && (
                <div className="absolute left-full ml-2 px-2 py-1 bg-popover text-popover-foreground text-xs rounded shadow-md opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap z-50">
                  {item.name}
                </div>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="px-3 py-4 border-t border-[hsl(var(--sidebar-border))] space-y-3">
        <div className={cn("flex items-center justify-between px-3", isCollapsed ? "flex-col gap-4" : "")}>
          <ThemeToggle />
          <div className={cn("transition-all duration-300", isCollapsed ? "w-0 opacity-0 hidden" : "w-auto opacity-100")}>
            <UserMenu />
          </div>
        </div>
      </div>
    </aside>
  );
}
