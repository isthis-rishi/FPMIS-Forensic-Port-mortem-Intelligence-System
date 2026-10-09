'use client';

import { useState } from 'react';
import Link from 'next/link';
import { searchApi } from '@/lib/api';
import { SearchResult, SearchFilters } from '@/types';
import { formatDate, getStatusColor, getMannerOfDeathColor } from '@/lib/utils';
import { Search, Filter, X, User, ChevronLeft, ChevronRight } from 'lucide-react';

export default function SearchPage() {
  const [results, setResults] = useState<SearchResult[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  const [filters, setFilters] = useState<SearchFilters>({
    keyword: '',
    status: '',
    case_type: '',
    gender: '',
    age_min: undefined,
    age_max: undefined,
    district: '',
    manner_of_death: '',
  });

  const pageSize = 20;

  const handleSearch = async (newPage = 1) => {
    setIsLoading(true);
    setHasSearched(true);
    try {
      const cleanFilters = Object.fromEntries(
        Object.entries(filters).filter(([_, v]) => v !== '' && v !== undefined)
      );
      const data = await searchApi.search(cleanFilters, newPage, pageSize);
      setResults(data.results);
      setTotal(data.total);
      setPage(newPage);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFilterChange = (key: keyof SearchFilters, value: any) => {
    setFilters({ ...filters, [key]: value });
  };

  const clearFilters = () => {
    setFilters({
      keyword: '',
      status: '',
      case_type: '',
      gender: '',
      age_min: undefined,
      age_max: undefined,
      district: '',
      manner_of_death: '',
    });
  };

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div>
      {}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Search Cases</h1>
        <p className="text-gray-600">Search the forensic intelligence database</p>
      </div>

      {}
      <div className="card mb-6">
        <div className="card-body">
          <div className="flex gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={filters.keyword}
                onChange={(e) => handleFilterChange('keyword', e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                placeholder="Search by case number, name, identification marks..."
                className="input pl-10"
              />
            </div>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`btn-secondary flex items-center gap-2 ${showFilters ? 'bg-gray-200' : ''}`}
            >
              <Filter className="w-5 h-5" />
              Filters
            </button>
            <button onClick={() => handleSearch()} className="btn-primary">
              Search
            </button>
          </div>

          {}
          {showFilters && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <label className="label">Status</label>
                  <select
                    value={filters.status}
                    onChange={(e) => handleFilterChange('status', e.target.value)}
                    className="input"
                  >
                    <option value="">Any</option>
                    <option value="open">Open</option>
                    <option value="in_progress">In Progress</option>
                    <option value="completed">Completed</option>
                    <option value="closed">Closed</option>
                  </select>
                </div>
                <div>
                  <label className="label">Case Type</label>
                  <select
                    value={filters.case_type}
                    onChange={(e) => handleFilterChange('case_type', e.target.value)}
                    className="input"
                  >
                    <option value="">Any</option>
                    <option value="medico_legal">Medico Legal</option>
                    <option value="natural_death">Natural Death</option>
                    <option value="accident">Accident</option>
                    <option value="crime">Crime</option>
                    <option value="homicide">Homicide</option>
                  </select>
                </div>
                <div>
                  <label className="label">Gender</label>
                  <select
                    value={filters.gender}
                    onChange={(e) => handleFilterChange('gender', e.target.value)}
                    className="input"
                  >
                    <option value="">Any</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="transgender">Transgender</option>
                    <option value="unknown">Unknown</option>
                  </select>
                </div>
                <div>
                  <label className="label">Manner of Death</label>
                  <select
                    value={filters.manner_of_death}
                    onChange={(e) => handleFilterChange('manner_of_death', e.target.value)}
                    className="input"
                  >
                    <option value="">Any</option>
                    <option value="natural">Natural</option>
                    <option value="accident">Accident</option>
                    <option value="suicide">Suicide</option>
                    <option value="homicide">Homicide</option>
                    <option value="undetermined">Undetermined</option>
                  </select>
                </div>
                <div>
                  <label className="label">Age Min</label>
                  <input
                    type="number"
                    value={filters.age_min || ''}
                    onChange={(e) => handleFilterChange('age_min', e.target.value ? parseInt(e.target.value) : undefined)}
                    className="input"
                    placeholder="0"
                    min="0"
                  />
                </div>
                <div>
                  <label className="label">Age Max</label>
                  <input
                    type="number"
                    value={filters.age_max || ''}
                    onChange={(e) => handleFilterChange('age_max', e.target.value ? parseInt(e.target.value) : undefined)}
                    className="input"
                    placeholder="150"
                    max="150"
                  />
                </div>
                <div>
                  <label className="label">District</label>
                  <input
                    type="text"
                    value={filters.district}
                    onChange={(e) => handleFilterChange('district', e.target.value)}
                    className="input"
                    placeholder="Enter district"
                  />
                </div>
                <div className="flex items-end">
                  <button onClick={clearFilters} className="btn-secondary flex items-center gap-2">
                    <X className="w-4 h-4" />
                    Clear Filters
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {}
      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      ) : !hasSearched ? (
        <div className="card">
          <div className="card-body text-center py-16">
            <Search className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900">Search the Database</h3>
            <p className="text-gray-500 mt-2">Enter keywords or use filters to find cases</p>
          </div>
        </div>
      ) : results.length === 0 ? (
        <div className="card">
          <div className="card-body text-center py-16">
            <p className="text-gray-500">No results found. Try adjusting your search criteria.</p>
          </div>
        </div>
      ) : (
        <>
          <p className="text-sm text-gray-600 mb-4">Found {total} results</p>
          <div className="card">
            <div className="table-container">
              <table className="table">
                <thead>
                  <tr>
                    <th>Case Number</th>
                    <th>Deceased</th>
                    <th>Status</th>
                    <th>Manner of Death</th>
                    <th>District</th>
                    <th>Date</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {results.map((result) => (
                    <tr key={result.id}>
                      <td className="font-medium">{result.case_number}</td>
                      <td>
                        <div className="flex items-center gap-2">
                          {!result.is_identified && (
                            <User className="w-4 h-4 text-gray-400" />
                          )}
                          <div>
                            <p>{result.deceased_name || 'Unidentified'}</p>
                            <p className="text-xs text-gray-500">
                              {result.deceased_gender}, {result.deceased_age || '?'} yrs
                            </p>
                          </div>
                        </div>
                      </td>
                      <td>
                        <span className={`badge ${getStatusColor(result.status)}`}>
                          {result.status.replace('_', ' ')}
                        </span>
                      </td>
                      <td>
                        {result.manner_of_death ? (
                          <span className={`badge ${getMannerOfDeathColor(result.manner_of_death)}`}>
                            {result.manner_of_death}
                          </span>
                        ) : (
                          '-'
                        )}
                      </td>
                      <td>{result.district || '-'}</td>
                      <td>{formatDate(result.created_at)}</td>
                      <td>
                        <Link href={`/cases/${result.id}`} className="text-primary-600 hover:underline">
                          View
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {}
            {totalPages > 1 && (
              <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
                <p className="text-sm text-gray-600">
                  Page {page} of {totalPages}
                </p>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleSearch(page - 1)}
                    disabled={page === 1}
                    className="btn-secondary p-2 disabled:opacity-50"
                  >
                    <ChevronLeft className="w-5 h-5" />
                  </button>
                  <button
                    onClick={() => handleSearch(page + 1)}
                    disabled={page === totalPages}
                    className="btn-secondary p-2 disabled:opacity-50"
                  >
                    <ChevronRight className="w-5 h-5" />
                  </button>
                </div>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
