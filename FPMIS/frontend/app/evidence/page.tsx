'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { evidenceApi } from '@/lib/api';
import { Evidence } from '@/types';
import { formatDateTime, getStatusColor } from '@/lib/utils';
import { Package, ArrowRight, MapPin } from 'lucide-react';

export default function EvidencePage() {
  const [myEvidence, setMyEvidence] = useState<Evidence[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchMyEvidence();
  }, []);

  const fetchMyEvidence = async () => {
    try {
      const data = await evidenceApi.getMyEvidence();
      setMyEvidence(data);
    } catch (error) {
      console.error('Failed to fetch evidence:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      {}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">My Evidence</h1>
        <p className="text-gray-600">Evidence items currently in your custody</p>
      </div>

      {}
      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      ) : myEvidence.length === 0 ? (
        <div className="card">
          <div className="card-body text-center py-16">
            <Package className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900">No Evidence in Custody</h3>
            <p className="text-gray-500 mt-2">You don&apos;t have any evidence items assigned to you</p>
          </div>
        </div>
      ) : (
        <div className="grid gap-4">
          {myEvidence.map((item) => (
            <div key={item.id} className="card hover:shadow-md transition-shadow">
              <div className="card-body">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4">
                    <div className="p-3 bg-blue-100 rounded-lg">
                      <Package className="w-6 h-6 text-blue-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">{item.item_name}</h3>
                      <p className="text-sm text-gray-500">Evidence #{item.evidence_number}</p>
                      <p className="text-sm text-gray-600 mt-1">{item.description}</p>
                      <div className="flex items-center gap-4 mt-2">
                        <span className="text-xs text-gray-500 capitalize">
                          Type: {item.item_type.replace('_', ' ')}
                        </span>
                        {item.current_location && (
                          <span className="text-xs text-gray-500 flex items-center gap-1">
                            <MapPin className="w-3 h-3" />
                            {item.current_location}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-2">
                    <span className={`badge ${getStatusColor(item.status)}`}>
                      {item.status.replace('_', ' ')}
                    </span>
                    <p className="text-xs text-gray-500">
                      Collected: {formatDateTime(item.collected_at)}
                    </p>
                  </div>
                </div>
                <div className="mt-4 pt-4 border-t border-gray-100 flex justify-end">
                  <Link
                    href={`/cases/${item.case_id}?tab=evidence`}
                    className="text-primary-600 hover:underline flex items-center gap-1 text-sm"
                  >
                    View Case <ArrowRight className="w-4 h-4" />
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
