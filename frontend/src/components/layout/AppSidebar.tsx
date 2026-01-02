import { NavLink as RouterNavLink, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  Shield,
  FlaskConical,
  TrendingUp,
  Map,
  Trophy,
  Lightbulb,
  AlertTriangle,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { useState } from "react";

const navItems = [
  { title: "Dashboard", path: "/", icon: LayoutDashboard },
  { title: "Safety Check", path: "/safety-check", icon: Shield },
  { title: "Simulation", path: "/simulation", icon: FlaskConical },
  { title: "Crime Trends", path: "/trends", icon: TrendingUp },
  { title: "Heatmap", path: "/heatmap", icon: Map },
  { title: "Leaderboard", path: "/leaderboard", icon: Trophy },
  { title: "Recommendations", path: "/recommendations", icon: Lightbulb },
  { title: "SOS Emergency", path: "/sos", icon: AlertTriangle, critical: true },
];

export function AppSidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();

  return (
    <aside
      className={cn(
        "flex flex-col h-screen bg-sidebar border-r border-sidebar-border transition-all duration-300",
        collapsed ? "w-16" : "w-64"
      )}
    >
      {/* Logo */}
      <div className="flex items-center gap-3 p-4 border-b border-sidebar-border">
        <div className="flex items-center justify-center w-10 h-10 rounded-lg gradient-bg shrink-0">
          <Shield className="w-5 h-5 text-primary-foreground" />
        </div>
        {!collapsed && (
          <div className="flex flex-col min-w-0">
            <span className="font-bold text-lg gradient-text truncate">AI-GUARD</span>
            <span className="text-xs text-muted-foreground truncate">Women Safety</span>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          const Icon = item.icon;

          return (
            <RouterNavLink
              key={item.path}
              to={item.path}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group",
                isActive
                  ? "bg-primary/20 text-primary"
                  : "text-muted-foreground hover:text-foreground hover:bg-sidebar-accent",
                item.critical && !isActive && "text-destructive hover:text-destructive",
                collapsed && "justify-center px-2"
              )}
            >
              <Icon
                className={cn(
                  "w-5 h-5 shrink-0 transition-transform group-hover:scale-110",
                  item.critical && "text-destructive"
                )}
              />
              {!collapsed && (
                <span className={cn("text-sm font-medium truncate", item.critical && "text-destructive")}>
                  {item.title}
                </span>
              )}
              {item.critical && !collapsed && (
                <span className="ml-auto flex h-2 w-2 rounded-full bg-destructive animate-pulse-glow" />
              )}
            </RouterNavLink>
          );
        })}
      </nav>

      {/* Collapse Toggle */}
      <div className="p-3 border-t border-sidebar-border">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setCollapsed(!collapsed)}
          className={cn("w-full justify-center", !collapsed && "justify-start")}
        >
          {collapsed ? (
            <ChevronRight className="w-4 h-4" />
          ) : (
            <>
              <ChevronLeft className="w-4 h-4 mr-2" />
              <span>Collapse</span>
            </>
          )}
        </Button>
      </div>
    </aside>
  );
}
