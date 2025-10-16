import React, { useEffect, useState, useRef } from "react";
import {
  Home,
  Book,
  Calendar,
  Bell,
  Users,
  MessageCircle,
  User,
  Settings,
  Moon,
  LogOut,
  ChevronRight,
} from "lucide-react";
interface NavbarProps {
  toggleChat: () => void;
  isChatOpen: boolean;
}
export function Navbar({ toggleChat, isChatOpen }: NavbarProps) {
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const userMenuRef = useRef<HTMLDivElement>(null);
  // Handle click outside to close menu
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        userMenuRef.current &&
        !userMenuRef.current.contains(event.target as Node)
      ) {
        setUserMenuOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);
  return (
    <nav className="w-full bg-white border-b border-border h-16 px-4 flex items-center justify-between shadow-sm">
      <div className="flex items-center">
        <h1 className="text-xl font-bold text-primary">StudentHub</h1>
      </div>
      <div className="flex items-center space-x-6">
        <NavItem icon={<Home size={20} />} label="Home" />
        <NavItem icon={<Book size={20} />} label="Courses" />
        <NavItem icon={<Calendar size={20} />} label="Schedule" />
        <NavItem icon={<Bell size={20} />} label="Notifications" />
        <NavItem icon={<Users size={20} />} label="Groups" />
        <NavItem
          icon={
            <MessageCircle
              size={20}
              className={isChatOpen ? "text-primary" : ""}
            />
          }
          label="Chat"
          onClick={toggleChat}
          active={isChatOpen}
        />
      </div>
      <div className="flex items-center relative" ref={userMenuRef}>
        <div
          className={`w-10 h-10 rounded-full ${
            userMenuOpen
              ? "bg-primary text-primary-foreground"
              : "bg-primary/10 text-primary"
          } flex items-center justify-center cursor-pointer transition-colors`}
          onClick={() => setUserMenuOpen(!userMenuOpen)}
        >
          <span className="font-semibold">JS</span>
        </div>
        {userMenuOpen && (
          <div className="absolute right-0 top-12 w-64 bg-white border border-border rounded-lg shadow-lg z-20 overflow-hidden">
            <div className="p-4 border-b border-border">
              <div className="flex items-center">
                <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mr-3">
                  <span className="font-semibold text-primary">JS</span>
                </div>
                <div>
                  <h4 className="font-semibold">John Smith</h4>
                  <p className="text-xs text-muted-foreground">
                    john.smith@university.edu
                  </p>
                </div>
              </div>
            </div>
            <div className="py-2">
              <UserMenuItem icon={<User size={18} />} label="View Profile" />
              <UserMenuItem
                icon={<Settings size={18} />}
                label="Account Settings"
              />
              <UserMenuItem
                icon={<Bell size={18} />}
                label="Notification Preferences"
              />
              <UserMenuItem
                icon={<Moon size={18} />}
                label="Dark Mode"
                toggle
              />
              <div className="border-t border-border my-1"></div>
              <UserMenuItem
                icon={<LogOut size={18} />}
                label="Sign Out"
                className="text-destructive"
              />
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}
interface NavItemProps {
  icon: React.ReactNode;
  label: string;
  onClick?: () => void;
  active?: boolean;
}
function NavItem({ icon, label, onClick, active }: NavItemProps) {
  return (
    <div
      className={`relative group cursor-pointer p-2 rounded-full hover:bg-secondary transition-all duration-200 ${
        active ? "bg-secondary" : ""
      }`}
      onClick={onClick}
    >
      {icon}
      <div className="absolute opacity-0 group-hover:opacity-100 invisible group-hover:visible right-0 top-1/2 translate-x-0 group-hover:translate-x-full -translate-y-1/2 bg-popover text-popover-foreground text-xs px-2 py-1 rounded-md whitespace-nowrap shadow-md z-10 transition-all duration-200">
        {label}
      </div>
    </div>
  );
}
interface UserMenuItemProps {
  icon: React.ReactNode;
  label: string;
  onClick?: () => void;
  className?: string;
  toggle?: boolean;
}
function UserMenuItem({
  icon,
  label,
  onClick,
  className = "",
  toggle = false,
}: UserMenuItemProps) {
  const [isToggled, setIsToggled] = useState(false);
  const handleToggle = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (toggle) {
      setIsToggled(!isToggled);
    }
    if (onClick) onClick();
  };
  return (
    <div
      className={`flex items-center justify-between px-4 py-2 hover:bg-secondary cursor-pointer ${className}`}
      onClick={handleToggle}
    >
      <div className="flex items-center">
        <span className="mr-3">{icon}</span>
        <span>{label}</span>
      </div>
      {toggle ? (
        <div
          className={`w-10 h-5 rounded-full ${
            isToggled ? "bg-primary" : "bg-muted"
          } relative transition-colors`}
        >
          <div
            className={`absolute w-4 h-4 rounded-full bg-white top-0.5 transition-transform ${
              isToggled ? "translate-x-5" : "translate-x-1"
            }`}
          />
        </div>
      ) : (
        <ChevronRight size={16} className="text-muted-foreground" />
      )}
    </div>
  );
}
