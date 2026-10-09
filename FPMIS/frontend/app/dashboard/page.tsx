'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { searchApi, alertsApi } from '@/lib/api';
import { useAuthStore } from '@/lib/auth-store';
import { DashboardStats, AlertStats } from '@/types';
import {
  FileText,
  Users,
  AlertTriangle,
  Clock,
  TrendingUp,
  ArrowRight,
  Activity,
} from 'lucide-react';

export default function DashboardPage() {
  const { user } = useAuthStore();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [alertStats, setAlertStats] = useState<AlertStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsData, alertsData] = await Promise.all([
          searchApi.getStats(),
          alertsApi.getStats(),
        ]);
        setStats(statsData);
        setAlertStats(alertsData);
      } catch (error) {
        console.error('Failed to fetch stats:', error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div>
      {}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">
          Welcome back, {user?.full_name?.split(' ')[0]}!
        </h1>
        <p className="text-gray-600 mt-1">
          Here&apos;s what&apos;s happening in your forensic intelligence system.
        </p>
      </div>

      {}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Total Cases"
          value={stats?.total_cases || 0}
          icon={FileText}
          color="blue"
          href="/cases"
        />
        <StatCard
          title="Open Cases"
          value={stats?.by_status?.open || 0}
          icon={Clock}
          color="yellow"
          href="/cases?status=open"
        />
        <StatCard
          title="Unidentified Bodies"
          value={stats?.identified_vs_unidentified?.unidentified || 0}
          icon={Users}
          color="purple"
          href="/search?unidentified=true"
        />
        <StatCard
          title="Active Alerts"
          value={(alertStats?.new || 0) + (alertStats?.investigating || 0)}
          icon={AlertTriangle}
          color="red"
          href="/alerts"
        />
      </div>

      {}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {}
        <div className="card">
          <div className="card-header flex justify-between items-center">
            <h2 className="font-semibold text-gray-900">Cases by Status</h2>
            <Activity className="w-5 h-5 text-gray-400" />
          </div>
          <div className="card-body">
            <div className="space-y-4">
              {Object.entries(stats?.by_status || {}).map(([status, count]) => (
                <div key={status}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="capitalize text-gray-600">{status.replace('_', ' ')}</span>
                    <span className="font-medium">{count}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-primary-600 h-2 rounded-full"
                      style={{
                        width: `${((count as number) / (stats?.total_cases || 1)) * 100}%`,
                      }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {}
        <div className="card">
          <div className="card-header flex justify-between items-center">
            <h2 className="font-semibold text-gray-900">Manner of Death</h2>
            <TrendingUp className="w-5 h-5 text-gray-400" />
          </div>
          <div className="card-body">
            <div className="grid grid-cols-2 gap-4">
              {Object.entries(stats?.by_manner_of_death || {}).map(([manner, count]) => (
                <div key={manner} className="p-3 bg-gray-50 rounded-lg">
                  <p className="text-2xl font-bold text-gray-900">{count}</p>
                  <p className="text-sm text-gray-600 capitalize">{manner}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {}
      <div className="card">
        <div className="card-header">
          <h2 className="font-semibold text-gray-900">Quick Actions</h2>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link
              href="/cases/new"
              className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors"
            >
              <div>
                <p className="font-medium text-gray-900">New Case</p>
                <p className="text-sm text-gray-500">Register a new case</p>
              </div>
              <ArrowRight className="w-5 h-5 text-gray-400" />
            </Link>
            <Link
              href="/missing-persons/new"
              className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors"
            >
              <div>
                <p className="font-medium text-gray-900">Missing Person Report</p>
                <p className="text-sm text-gray-500">Add missing person</p>
              </div>
              <ArrowRight className="w-5 h-5 text-gray-400" />
            </Link>
            <Link
              href="/alerts"
              className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors"
            >
              <div>
                <p className="font-medium text-gray-900">Run Alert Detection</p>
                <p className="text-sm text-gray-500">Check for patterns</p>
              </div>
              <ArrowRight className="w-5 h-5 text-gray-400" />
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({
  title,
  value,
  icon: Icon,
  color,
  href,
}: {
  title: string;
  value: number;
  icon: any;
  color: 'blue' | 'yellow' | 'purple' | 'red';
  href: string;
}) {
  const colors = {
    blue: 'bg-blue-100 text-blue-600',
    yellow: 'bg-yellow-100 text-yellow-600',
    purple: 'bg-purple-100 text-purple-600',
    red: 'bg-red-100 text-red-600',
  };

  return (
    <Link href={href} className="card hover:shadow-md transition-shadow">
      <div className="card-body flex items-center gap-4">
        <div className={`p-3 rounded-xl ${colors[color]}`}>
          <Icon className="w-6 h-6" />
        </div>
        <div>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          <p className="text-sm text-gray-600">{title}</p>
        </div>
      </div>
    </Link>
  );
}
