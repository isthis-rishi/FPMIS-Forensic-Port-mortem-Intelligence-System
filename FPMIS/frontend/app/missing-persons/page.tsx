'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { missingPersonsApi } from '@/lib/api';
import { MissingPerson } from '@/types';
import { formatDate, getStatusColor } from '@/lib/utils';
import { Plus, Search, Users, MapPin, Calendar } from 'lucide-react';

export default function MissingPersonsPage() {
  const [persons, setPersons] = useState<MissingPerson[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('active');

  useEffect(() => {
    fetchPersons();
  }, [statusFilter]);

  const fetchPersons = async () => {
    setIsLoading(true);
    try {
      const data = await missingPersonsApi.list({
        status: statusFilter || undefined,
        search: search || undefined,
      });
      setPersons(data);
    } catch (error) {
      console.error('Failed to fetch:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchPersons();
  };

  return (
    <div>
      {}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Missing Persons</h1>
          <p className="text-gray-600">Manage missing person reports for body matching</p>
        </div>
        <Link href="/missing-persons/new" className="btn-primary flex items-center gap-2">
          <Plus className="w-5 h-5" />
          New Report
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
                  placeholder="Search by name..."
                  className="input pl-10"
                />
              </div>
            </form>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="input w-auto"
            >
              <option value="">All Statuses</option>
              <option value="active">Active</option>
              <option value="found_alive">Found Alive</option>
              <option value="found_deceased">Found Deceased</option>
              <option value="closed">Closed</option>
            </select>
          </div>
        </div>
      </div>

      {}
      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      ) : persons.length === 0 ? (
        <div className="card">
          <div className="card-body text-center py-16">
            <Users className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900">No Missing Persons Found</h3>
            <p className="text-gray-500 mt-2">No reports match your criteria</p>
          </div>
        </div>
      ) : (
        <div className="grid gap-4">
          {persons.map((person) => (
            <div key={person.id} className="card hover:shadow-md transition-shadow">
              <div className="card-body">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 bg-gray-200 rounded-full flex items-center justify-center">
                      <Users className="w-6 h-6 text-gray-500" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">{person.name}</h3>
                      <p className="text-sm text-gray-500">Report #{person.report_number}</p>
                      <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
                        <span className="capitalize">{person.gender}</span>
                        {person.age_years && <span>{person.age_years} years old</span>}
                      </div>
                      <div className="flex items-center gap-4 mt-2 text-sm text-gray-500">
                        <span className="flex items-center gap-1">
                          <Calendar className="w-4 h-4" />
                          Last seen: {formatDate(person.last_seen_date)}
                        </span>
                        {person.last_seen_location && (
                          <span className="flex items-center gap-1">
                            <MapPin className="w-4 h-4" />
                            {person.last_seen_location}
                          </span>
                        )}
                      </div>
                      {person.identification_marks && (
                        <p className="text-sm text-gray-600 mt-2">
                          Marks: {person.identification_marks}
                        </p>
                      )}
                    </div>
                  </div>
                  <span className={`badge ${getStatusColor(person.status)}`}>
                    {person.status.replace('_', ' ')}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
