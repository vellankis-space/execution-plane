import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { User as UserIcon, LogOut } from "lucide-react";
import { useNavigate } from "react-router-dom";

export function UserMenu() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  if (!user) return null;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="sm" className="flex items-center gap-2 text-[hsl(var(--sidebar-foreground))]/70 hover:text-[hsl(var(--sidebar-foreground))] hover:bg-[hsl(var(--sidebar-foreground))]/10">
          <UserIcon className="h-4 w-4" />
          <span className="hidden sm:inline">{user.username}</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        <DropdownMenuLabel>
          <div className="flex flex-col space-y-1">
            <p className="text-sm font-medium">{user.full_name || user.username}</p>
            <p className="text-xs text-muted-foreground">{user.email}</p>
          </div>
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        {user.roles && user.roles.length > 0 && (
          <>
            <DropdownMenuLabel className="text-xs">Roles</DropdownMenuLabel>
            {user.roles.map((role) => (
              <DropdownMenuItem key={role} disabled>
                {role}
              </DropdownMenuItem>
            ))}
            <DropdownMenuSeparator />
          </>
        )}
        <DropdownMenuItem onClick={handleLogout}>
          <LogOut className="mr-2 h-4 w-4" />
          Log out
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

