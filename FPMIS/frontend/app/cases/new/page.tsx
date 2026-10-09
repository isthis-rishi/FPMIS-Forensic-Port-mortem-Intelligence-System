'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { casesApi } from '@/lib/api';
import { ArrowLeft, Save, AlertCircle } from 'lucide-react';
import Link from 'next/link';
import api from '@/lib/api';

interface Institution {
  id: string;
  name: string;
  type: string;
}

export default function NewCasePage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [institutions, setInstitutions] = useState<Institution[]>([]);

  const [formData, setFormData] = useState({
    case_type: 'medico_legal',
    priority: 'normal',
    police_station: '',
    fir_number: '',
    brought_by: '',
    institution_id: '',
    is_identified: false,
    name: '',
    age_years: '',
    gender: 'unknown',
    height_cm: '',
    weight_kg: '',
    identification_marks: '',
    district: '',
  });

  useEffect(() => {
    const fetchInstitutions = async () => {
      try {
        const response = await api.get('/api/institutions');
        setInstitutions(response.data);
        if (response.data.length > 0) {
          setFormData(prev => ({ ...prev, institution_id: response.data[0].id }));
        }
      } catch (err) {
        setFormData(prev => ({ ...prev, institution_id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890' }));
      }
    };
    fetchInstitutions();
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const caseData = {
        institution_id: formData.institution_id || 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
        case_type: formData.case_type,
        priority: formData.priority,
        police_station: formData.police_station || undefined,
        fir_number: formData.fir_number || undefined,
        brought_by: formData.brought_by || undefined,
        deceased_info: {
          is_identified: formData.is_identified,
          name: formData.name || undefined,
          age_years: formData.age_years ? parseInt(formData.age_years) : undefined,
          gender: formData.gender,
          height_cm: formData.height_cm ? parseFloat(formData.height_cm) : undefined,
          weight_kg: formData.weight_kg ? parseFloat(formData.weight_kg) : undefined,
          identification_marks: formData.identification_marks || undefined,
          district: formData.district || undefined,
        },
      };

      const newCase = await casesApi.create(caseData);
      router.push(`/cases/${newCase.id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create case');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-3xl">
      {}
      <div className="flex items-center gap-4 mb-6">
        <Link href="/cases" className="p-2 hover:bg-gray-100 rounded-lg">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">New Case</h1>
          <p className="text-gray-600">Register a new forensic case</p>
        </div>
      </div>

      {error && (
        <div className="mb-6 flex items-center gap-2 p-4 bg-red-50 text-red-700 rounded-lg">
          <AlertCircle className="w-5 h-5" />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit}>
        {}
        <div className="card mb-6">
          <div className="card-header">
            <h2 className="font-semibold">Case Details</h2>
          </div>
          <div className="card-body space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="label">Case Type</label>
                <select
                  name="case_type"
                  value={formData.case_type}
                  onChange={handleChange}
                  className="input"
                >
                  <option value="medico_legal">Medico Legal</option>
                  <option value="natural_death">Natural Death</option>
                  <option value="accident">Accident</option>
                  <option value="crime">Crime</option>
                  <option value="mass_disaster">Mass Disaster</option>
                  <option value="unknown">Unknown</option>
                </select>
              </div>
              <div>
                <label className="label">Priority</label>
                <select
                  name="priority"
                  value={formData.priority}
                  onChange={handleChange}
                  className="input"
                >
                  <option value="low">Low</option>
                  <option value="normal">Normal</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="label">Police Station</label>
                <input
                  type="text"
                  name="police_station"
                  value={formData.police_station}
                  onChange={handleChange}
                  className="input"
                  placeholder="Enter police station name"
                />
              </div>
              <div>
                <label className="label">FIR Number</label>
                <input
                  type="text"
                  name="fir_number"
                  value={formData.fir_number}
                  onChange={handleChange}
                  className="input"
                  placeholder="Enter FIR number"
                />
              </div>
            </div>

            <div>
              <label className="label">Brought By</label>
              <input
                type="text"
                name="brought_by"
                value={formData.brought_by}
                onChange={handleChange}
                className="input"
                placeholder="Name of person/authority who brought the body"
              />
            </div>
          </div>
        </div>

        {}
        <div className="card mb-6">
          <div className="card-header">
            <h2 className="font-semibold">Deceased Information</h2>
          </div>
          <div className="card-body space-y-4">
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="is_identified"
                name="is_identified"
                checked={formData.is_identified}
                onChange={handleChange}
                className="w-4 h-4 text-primary-600"
              />
              <label htmlFor="is_identified" className="text-sm">
                Body is identified
              </label>
            </div>

            {formData.is_identified && (
              <div>
                <label className="label">Name</label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  className="input"
                  placeholder="Full name of deceased"
                />
              </div>
            )}

            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="label">Age (Years)</label>
                <input
                  type="number"
                  name="age_years"
                  value={formData.age_years}
                  onChange={handleChange}
                  className="input"
                  placeholder="Estimated age"
                  min="0"
                  max="150"
                />
              </div>
              <div>
                <label className="label">Gender</label>
                <select
                  name="gender"
                  value={formData.gender}
                  onChange={handleChange}
                  className="input"
                >
                  <option value="unknown">Unknown</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="transgender">Transgender</option>
                </select>
              </div>
              <div>
                <label className="label">District</label>
                <input
                  type="text"
                  name="district"
                  value={formData.district}
                  onChange={handleChange}
                  className="input"
                  placeholder="District"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="label">Height (cm)</label>
                <input
                  type="number"
                  name="height_cm"
                  value={formData.height_cm}
                  onChange={handleChange}
                  className="input"
                  placeholder="Height in cm"
                  step="0.1"
                />
              </div>
              <div>
                <label className="label">Weight (kg)</label>
                <input
                  type="number"
                  name="weight_kg"
                  value={formData.weight_kg}
                  onChange={handleChange}
                  className="input"
                  placeholder="Weight in kg"
                  step="0.1"
                />
              </div>
            </div>

            <div>
              <label className="label">Identification Marks</label>
              <textarea
                name="identification_marks"
                value={formData.identification_marks}
                onChange={handleChange}
                className="input min-h-[100px]"
                placeholder="Scars, tattoos, birthmarks, deformities..."
              />
            </div>
          </div>
        </div>

        {}
        <div className="flex justify-end gap-4">
          <Link href="/cases" className="btn-secondary">
            Cancel
          </Link>
          <button type="submit" disabled={isLoading} className="btn-primary flex items-center gap-2">
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                Creating...
              </>
            ) : (
              <>
                <Save className="w-5 h-5" />
                Create Case
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
