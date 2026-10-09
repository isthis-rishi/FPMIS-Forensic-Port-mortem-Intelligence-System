'use client';

import { useEffect, useState } from 'react';
import { alertsApi } from '@/lib/api';
import { Alert, AlertStats } from '@/types';
import { formatDateTime, getSeverityColor, getStatusColor } from '@/lib/utils';
import { Bell, RefreshCw, AlertTriangle, CheckCircle, Clock, Eye, XCircle } from 'lucide-react';

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [stats, setStats] = useState<AlertStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isDetecting, setIsDetecting] = useState(false);
  const [statusFilter, setStatusFilter] = useState('');
  const [severityFilter, setSeverityFilter] = useState('');

  useEffect(() => {
    fetchData();
  }, [statusFilter, severityFilter]);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const [alertsData, statsData] = await Promise.all([
        alertsApi.list({
          status: statusFilter || undefined,
          severity: severityFilter || undefined,
        }),
        alertsApi.getStats(),
      ]);
      setAlerts(alertsData);
      setStats(statsData);
    } catch (error) {
      console.error('Failed to fetch alerts:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const runDetection = async () => {
    setIsDetecting(true);
    try {
      const newAlerts = await alertsApi.detect();
      if (newAlerts.length > 0) {
        alert(`Found ${newAlerts.length} new alerts!`);
        fetchData();
      } else {
        alert('No new patterns detected.');
      }
    } catch (error) {
      console.error('Detection failed:', error);
    } finally {
      setIsDetecting(false);
    }
  };

  const updateStatus = async (alertId: string, newStatus: string) => {
    try {
      await alertsApi.updateStatus(alertId, newStatus);
      fetchData();
    } catch (error) {
      console.error('Failed to update status:', error);
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <AlertTriangle className="w-5 h-5 text-red-500" />;
      case 'high':
        return <AlertTriangle className="w-5 h-5 text-orange-500" />;
      case 'medium':
        return <Clock className="w-5 h-5 text-yellow-500" />;
      default:
        return <Bell className="w-5 h-5 text-gray-500" />;
    }
  };

  return (
    <div>
      {}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Alerts</h1>
          <p className="text-gray-600">Pattern detection and notifications</p>
        </div>
        <button
          onClick={runDetection}
          disabled={isDetecting}
          className="btn-primary flex items-center gap-2"
        >
          <RefreshCw className={`w-5 h-5 ${isDetecting ? 'animate-spin' : ''}`} />
          {isDetecting ? 'Detecting...' : 'Run Detection'}
        </button>
      </div>

      {}
      {stats && (
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="card">
            <div className="card-body text-center">
              <p className="text-3xl font-bold text-red-600">{stats.new}</p>
              <p className="text-sm text-gray-600">New Alerts</p>
            </div>
          </div>
          <div className="card">
            <div className="card-body text-center">
              <p className="text-3xl font-bold text-yellow-600">{stats.investigating}</p>
              <p className="text-sm text-gray-600">Investigating</p>
            </div>
          </div>
          <div className="card">
            <div className="card-body text-center">
              <p className="text-3xl font-bold text-green-600">{stats.resolved}</p>
              <p className="text-sm text-gray-600">Resolved</p>
            </div>
          </div>
          <div className="card">
            <div className="card-body text-center">
              <p className="text-3xl font-bold text-gray-600">{stats.total}</p>
              <p className="text-sm text-gray-600">Total</p>
            </div>
          </div>
        </div>
      )}

      {}
      <div className="card mb-6">
        <div className="card-body">
          <div className="flex gap-4">
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="input w-auto"
            >
              <option value="">All Statuses</option>
              <option value="new">New</option>
              <option value="viewed">Viewed</option>
              <option value="investigating">Investigating</option>
              <option value="resolved">Resolved</option>
              <option value="dismissed">Dismissed</option>
            </select>
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="input w-auto"
            >
              <option value="">All Severities</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
        </div>
      </div>

      {}
      <div className="space-y-4">
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        ) : alerts.length === 0 ? (
          <div className="card">
            <div className="card-body text-center py-12">
              <Bell className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">No alerts found</p>
            </div>
          </div>
        ) : (
          alerts.map((alert) => (
            <div key={alert.id} className="card hover:shadow-md transition-shadow">
              <div className="card-body">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0 mt-1">
                    {getSeverityIcon(alert.severity)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <h3 className="font-semibold text-gray-900">{alert.title}</h3>
                        <p className="text-sm text-gray-600 mt-1">{alert.description}</p>
                        {alert.region && (
                          <p className="text-sm text-gray-500 mt-1">Region: {alert.region}</p>
                        )}
                        {alert.pattern_details && (
                          <p className="text-sm text-gray-500 mt-1">{alert.pattern_details}</p>
                        )}
                      </div>
                      <div className="flex flex-col items-end gap-2">
                        <span className={`badge ${getSeverityColor(alert.severity)}`}>
                          {alert.severity}
                        </span>
                        <span className={`badge ${getStatusColor(alert.status)}`}>
                          {alert.status}
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-100">
                      <p className="text-xs text-gray-500">
                        {formatDateTime(alert.generated_at)}
                      </p>
                      <div className="flex gap-2">
                        {alert.status === 'new' && (
                          <button
                            onClick={() => updateStatus(alert.id, 'investigating')}
                            className="btn-secondary text-sm py-1 px-3 flex items-center gap-1"
                          >
                            <Eye className="w-4 h-4" />
                            Investigate
                          </button>
                        )}
                        {alert.status === 'investigating' && (
                          <button
                            onClick={() => updateStatus(alert.id, 'resolved')}
                            className="btn-success text-sm py-1 px-3 flex items-center gap-1"
                          >
                            <CheckCircle className="w-4 h-4" />
                            Resolve
                          </button>
                        )}
                        {(alert.status === 'new' || alert.status === 'investigating') && (
                          <button
                            onClick={() => updateStatus(alert.id, 'dismissed')}
                            className="text-sm py-1 px-3 text-gray-500 hover:text-gray-700"
                          >
                            Dismiss
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
