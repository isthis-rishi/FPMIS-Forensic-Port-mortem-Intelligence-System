'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import {
  Shield,
  LayoutDashboard,
  FileText,
  Package,
  Clock,
  Search,
  Bell,
  Users,
  Settings,
  LogOut,
  Menu,
  X,
} from 'lucide-react';
import { useAuthStore } from '@/lib/auth-store';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Cases', href: '/cases', icon: FileText },
  { name: 'Evidence', href: '/evidence', icon: Package },
  { name: 'Missing Persons', href: '/missing-persons', icon: Users },
  { name: 'Search', href: '/search', icon: Search },
  { name: 'Alerts', href: '/alerts', icon: Bell },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuthStore();
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    setMobileOpen(false);
  }, [pathname]);

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 1024) {
        setMobileOpen(false);
      }
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const sidebarContent = (
    <>
      {}
      <div className="flex items-center gap-3 px-6 py-5 border-b border-gray-800">
        <div className="w-10 h-10 bg-primary-600 rounded-xl flex items-center justify-center flex-shrink-0">
          <Shield className="w-6 h-6" />
        </div>
        <div>
          <h1 className="font-bold">FPMIS</h1>
          <p className="text-xs text-gray-400">Intelligence System</p>
        </div>
        {}
        <button
          onClick={() => setMobileOpen(false)}
          className="lg:hidden ml-auto p-1 text-gray-400 hover:text-white"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {}
      <nav className="px-3 py-4 space-y-1 flex-1 overflow-y-auto">
        {navigation.map((item) => {
          const isActive = pathname.startsWith(item.href);
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors',
                isActive
                  ? 'bg-primary-600 text-white'
                  : 'text-gray-300 hover:bg-gray-800 hover:text-white'
              )}
            >
              <item.icon className="w-5 h-5 flex-shrink-0" />
              <span className="font-medium">{item.name}</span>
            </Link>
          );
        })}
      </nav>

      {}
      <div className="p-4 border-t border-gray-800">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-10 h-10 bg-gray-700 rounded-full flex items-center justify-center flex-shrink-0">
            <span className="text-sm font-medium">
              {user?.full_name?.charAt(0).toUpperCase() || 'U'}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">{user?.full_name || 'User'}</p>
            <p className="text-xs text-gray-400 capitalize">{user?.role?.replace('_', ' ')}</p>
          </div>
        </div>
        <button
          onClick={logout}
          className="flex items-center gap-2 w-full px-3 py-2 text-gray-300 hover:bg-gray-800 hover:text-white rounded-lg transition-colors"
        >
          <LogOut className="w-5 h-5" />
          <span>Sign Out</span>
        </button>
      </div>
    </>
  );

  return (
    <>
      {}
      <div className="lg:hidden fixed top-0 left-0 right-0 z-40 bg-gray-900 text-white flex items-center gap-3 px-4 py-3 shadow-lg">
        <button
          onClick={() => setMobileOpen(true)}
          className="p-1.5 rounded-lg hover:bg-gray-800 transition-colors"
          aria-label="Open menu"
        >
          <Menu className="w-6 h-6" />
        </button>
        <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
          <Shield className="w-5 h-5" />
        </div>
        <h1 className="font-bold text-sm">FPMIS</h1>
      </div>

      {}
      {mobileOpen && (
        <div
          className="lg:hidden fixed inset-0 z-40 bg-black/50"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {}
      <aside
        className={cn(
          'lg:hidden fixed inset-y-0 left-0 z-50 w-72 bg-gray-900 text-white flex flex-col transform transition-transform duration-300 ease-in-out',
          mobileOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        {sidebarContent}
      </aside>

      {}
      <aside className="hidden lg:flex fixed inset-y-0 left-0 w-64 bg-gray-900 text-white flex-col">
        {sidebarContent}
      </aside>
    </>
  );
}
