'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { casesApi } from '@/lib/api';
import { Case } from '@/types';
import { formatDate, getStatusColor, getPriorityColor } from '@/lib/utils';
import { Plus, Search, Filter, ChevronLeft, ChevronRight } from 'lucide-react';

export default function CasesPage() {
  const [cases, setCases] = useState<Case[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  const pageSize = 10;

  useEffect(() => {
    fetchCases();
  }, [page, statusFilter]);

  const fetchCases = async () => {
    setIsLoading(true);
    try {
      const data = await casesApi.list({
        page,
        status: statusFilter || undefined,
        search: search || undefined,
      });
      setCases(data.cases);
      setTotal(data.total);
    } catch (error) {
      console.error('Failed to fetch cases:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchCases();
  };

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div>
      {}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Cases</h1>
          <p className="text-gray-600">Manage forensic cases</p>
        </div>
        <Link href="/cases/new" className="btn-primary flex items-center gap-2">
          <Plus className="w-5 h-5" />
          New Case
        </Link>
      </div>

      {}
      <div className="card mb-6">
        <div className="card-body">
          <div className="flex flex-wrap gap-4">
            <form onSubmit={handleSearch} className="flex-1 min-w-[200px]">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Search cases..."
                  className="input pl-10"
                />
              </div>
            </form>
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setPage(1);
              }}
              className="input w-auto"
            >
              <option value="">All Statuses</option>
              <option value="open">Open</option>
              <option value="in_progress">In Progress</option>
              <option value="pending_review">Pending Review</option>
              <option value="completed">Completed</option>
              <option value="closed">Closed</option>
            </select>
          </div>
        </div>
      </div>

      {}
      <div className="card">
        <div className="table-container">
          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
            </div>
          ) : cases.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500">No cases found</p>
            </div>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>Case Number</th>
                  <th>Type</th>
                  <th>Status</th>
                  <th>Priority</th>
                  <th>Police Station</th>
                  <th>Created</th>
                  <th></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {cases.map((caseItem) => (
                  <tr key={caseItem.id}>
                    <td className="font-medium">{caseItem.case_number}</td>
                    <td className="capitalize">{caseItem.case_type?.replace('_', ' ') || '-'}</td>
                    <td>
                      <span className={`badge ${getStatusColor(caseItem.status)}`}>
                        {caseItem.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${getPriorityColor(caseItem.priority)}`}>
                        {caseItem.priority}
                      </span>
                    </td>
                    <td>{caseItem.police_station || '-'}</td>
                    <td>{formatDate(caseItem.created_at)}</td>
                    <td>
                      <Link
                        href={`/cases/${caseItem.id}`}
                        className="text-primary-600 hover:underline"
                      >
                        View
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {}
        {totalPages > 1 && (
          <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
            <p className="text-sm text-gray-600">
              Showing {(page - 1) * pageSize + 1} to {Math.min(page * pageSize, total)} of {total} cases
            </p>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setPage(page - 1)}
                disabled={page === 1}
                className="btn-secondary p-2 disabled:opacity-50"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
              <span className="px-3 py-1 text-sm">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => setPage(page + 1)}
                disabled={page === totalPages}
                className="btn-secondary p-2 disabled:opacity-50"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
