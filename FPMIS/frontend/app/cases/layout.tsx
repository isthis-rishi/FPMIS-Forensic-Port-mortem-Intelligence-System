'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Sidebar from '@/components/layouts/Sidebar';
import { useAuthStore } from '@/lib/auth-store';

export default function CasesLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const { user, checkAuth } = useAuthStore();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/auth/login');
    } else if (!user) {
      checkAuth();
    }
  }, [user, checkAuth, router]);

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar />
      <main className="pt-16 lg:pt-0 lg:ml-64 p-4 lg:p-8">{children}</main>
    </div>
  );
}
