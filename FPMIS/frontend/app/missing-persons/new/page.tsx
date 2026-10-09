'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { missingPersonsApi } from '@/lib/api';
import { ArrowLeft, Save, AlertCircle, User } from 'lucide-react';

export default function NewMissingPersonPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const [formData, setFormData] = useState({
    name: '',
    age_years: '',
    gender: 'unknown',
    height_cm_min: '',
    height_cm_max: '',
    weight_kg_min: '',
    weight_kg_max: '',
    build: '',
    hair_color: '',
    eye_color: '',
    complexion: '',
    identification_marks: '',
    scars: '',
    tattoos: '',
    birthmarks: '',
    deformities: '',
    last_seen_date: '',
    last_seen_location: '',
    last_seen_wearing: '',
    reporting_person_name: '',
    reporting_person_phone: '',
    reporting_person_relation: '',
    police_station: '',
    fir_number: '',
    additional_info: '',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const payload = {
        name: formData.name,
        reported_by: formData.reporting_person_name || 'Unknown',
        age_years: formData.age_years ? parseInt(formData.age_years) : undefined,
        gender: formData.gender,
        height_cm_min: formData.height_cm_min ? parseFloat(formData.height_cm_min) : undefined,
        height_cm_max: formData.height_cm_max ? parseFloat(formData.height_cm_max) : undefined,
        weight_kg_min: formData.weight_kg_min ? parseFloat(formData.weight_kg_min) : undefined,
        weight_kg_max: formData.weight_kg_max ? parseFloat(formData.weight_kg_max) : undefined,
        build: formData.build || undefined,
        hair_color: formData.hair_color || undefined,
        eye_color: formData.eye_color || undefined,
        complexion: formData.complexion || undefined,
        identification_marks: formData.identification_marks || undefined,
        scars: formData.scars || undefined,
        tattoos: formData.tattoos || undefined,
        birthmarks: formData.birthmarks || undefined,
        deformities: formData.deformities || undefined,
        last_seen_date: formData.last_seen_date || undefined,
        last_seen_location: formData.last_seen_location || undefined,
        last_seen_wearing: formData.last_seen_wearing || undefined,
        reporting_person_name: formData.reporting_person_name || undefined,
        reporting_person_phone: formData.reporting_person_phone || undefined,
        reporting_person_relation: formData.reporting_person_relation || undefined,
        police_station: formData.police_station || undefined,
        fir_number: formData.fir_number || undefined,
        additional_info: formData.additional_info || undefined,
      };

      await missingPersonsApi.create(payload);
      router.push('/missing-persons');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create missing person report');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl">
      {}
      <div className="flex items-center gap-4 mb-6">
        <Link href="/missing-persons" className="p-2 hover:bg-gray-100 rounded-lg">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">New Missing Person Report</h1>
          <p className="text-gray-600">Add a missing person to the database for body matching</p>
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
            <h2 className="font-semibold flex items-center gap-2">
              <User className="w-5 h-5" />
              Basic Information
            </h2>
          </div>
          <div className="card-body space-y-4">
            <div>
              <label className="label">Full Name *</label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                className="input"
                placeholder="Full name of missing person"
                required
              />
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div>
                <label className="label">Age (Years)</label>
                <input
                  type="number"
                  name="age_years"
                  value={formData.age_years}
                  onChange={handleChange}
                  className="input"
                  placeholder="Approximate age"
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
                <label className="label">Build</label>
                <select
                  name="build"
                  value={formData.build}
                  onChange={handleChange}
                  className="input"
                >
                  <option value="">Select...</option>
                  <option value="thin">Thin</option>
                  <option value="slim">Slim</option>
                  <option value="average">Average</option>
                  <option value="athletic">Athletic</option>
                  <option value="heavy">Heavy</option>
                  <option value="obese">Obese</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <label className="label">Height Min (cm)</label>
                <input
                  type="number"
                  name="height_cm_min"
                  value={formData.height_cm_min}
                  onChange={handleChange}
                  className="input"
                  placeholder="150"
                  step="0.1"
                />
              </div>
              <div>
                <label className="label">Height Max (cm)</label>
                <input
                  type="number"
                  name="height_cm_max"
                  value={formData.height_cm_max}
                  onChange={handleChange}
                  className="input"
                  placeholder="180"
                  step="0.1"
                />
              </div>
              <div>
                <label className="label">Weight Min (kg)</label>
                <input
                  type="number"
                  name="weight_kg_min"
                  value={formData.weight_kg_min}
                  onChange={handleChange}
                  className="input"
                  placeholder="50"
                  step="0.1"
                />
              </div>
              <div>
                <label className="label">Weight Max (kg)</label>
                <input
                  type="number"
                  name="weight_kg_max"
                  value={formData.weight_kg_max}
                  onChange={handleChange}
                  className="input"
                  placeholder="80"
                  step="0.1"
                />
              </div>
            </div>
          </div>
        </div>

        {}
        <div className="card mb-6">
          <div className="card-header">
            <h2 className="font-semibold">Physical Characteristics</h2>
          </div>
          <div className="card-body space-y-4">
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div>
                <label className="label">Hair Color</label>
                <select
                  name="hair_color"
                  value={formData.hair_color}
                  onChange={handleChange}
                  className="input"
                >
                  <option value="">Select...</option>
                  <option value="black">Black</option>
                  <option value="brown">Brown</option>
                  <option value="gray">Gray</option>
                  <option value="white">White</option>
                  <option value="bald">Bald</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <div>
                <label className="label">Eye Color</label>
                <select
                  name="eye_color"
                  value={formData.eye_color}
                  onChange={handleChange}
                  className="input"
                >
                  <option value="">Select...</option>
                  <option value="black">Black</option>
                  <option value="brown">Brown</option>
                  <option value="blue">Blue</option>
                  <option value="green">Green</option>
                  <option value="hazel">Hazel</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <div>
                <label className="label">Complexion</label>
                <select
                  name="complexion"
                  value={formData.complexion}
                  onChange={handleChange}
                  className="input"
                >
                  <option value="">Select...</option>
                  <option value="very_fair">Very Fair</option>
                  <option value="fair">Fair</option>
                  <option value="wheatish">Wheatish</option>
                  <option value="medium">Medium</option>
                  <option value="dark">Dark</option>
                  <option value="very_dark">Very Dark</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {}
        <div className="card mb-6">
          <div className="card-header">
            <h2 className="font-semibold">Identification Marks (Important for Matching)</h2>
          </div>
          <div className="card-body space-y-4">
            <div>
              <label className="label">General Identification Marks</label>
              <textarea
                name="identification_marks"
                value={formData.identification_marks}
                onChange={handleChange}
                className="input min-h-[80px]"
                placeholder="Any distinguishing features..."
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">Scars</label>
                <textarea
                  name="scars"
                  value={formData.scars}
                  onChange={handleChange}
                  className="input"
                  placeholder="Location and description of scars..."
                />
              </div>
              <div>
                <label className="label">Tattoos</label>
                <textarea
                  name="tattoos"
                  value={formData.tattoos}
                  onChange={handleChange}
                  className="input"
                  placeholder="Location and description of tattoos..."
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">Birthmarks</label>
                <textarea
                  name="birthmarks"
                  value={formData.birthmarks}
                  onChange={handleChange}
                  className="input"
                  placeholder="Location and description of birthmarks..."
                />
              </div>
              <div>
                <label className="label">Deformities</label>
                <textarea
                  name="deformities"
                  value={formData.deformities}
                  onChange={handleChange}
                  className="input"
                  placeholder="Any physical deformities..."
                />
              </div>
            </div>
          </div>
        </div>

        {}
        <div className="card mb-6">
          <div className="card-header">
            <h2 className="font-semibold">Last Seen Information</h2>
          </div>
          <div className="card-body space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">Last Seen Date</label>
                <input
                  type="date"
                  name="last_seen_date"
                  value={formData.last_seen_date}
                  onChange={handleChange}
                  className="input"
                />
              </div>
              <div>
                <label className="label">Last Seen Location</label>
                <input
                  type="text"
                  name="last_seen_location"
                  value={formData.last_seen_location}
                  onChange={handleChange}
                  className="input"
                  placeholder="City, area, or address"
                />
              </div>
            </div>

            <div>
              <label className="label">Last Seen Wearing</label>
              <textarea
                name="last_seen_wearing"
                value={formData.last_seen_wearing}
                onChange={handleChange}
                className="input"
                placeholder="Description of clothing..."
              />
            </div>
          </div>
        </div>

        {}
        <div className="card mb-6">
          <div className="card-header">
            <h2 className="font-semibold">Reporting Information</h2>
          </div>
          <div className="card-body space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="label">Reporter&apos;s Name</label>
                <input
                  type="text"
                  name="reporting_person_name"
                  value={formData.reporting_person_name}
                  onChange={handleChange}
                  className="input"
                  placeholder="Name of person reporting"
                />
              </div>
              <div>
                <label className="label">Reporter&apos;s Phone</label>
                <input
                  type="tel"
                  name="reporting_person_phone"
                  value={formData.reporting_person_phone}
                  onChange={handleChange}
                  className="input"
                  placeholder="+91 9876543210"
                />
              </div>
              <div>
                <label className="label">Relation to Missing Person</label>
                <input
                  type="text"
                  name="reporting_person_relation"
                  value={formData.reporting_person_relation}
                  onChange={handleChange}
                  className="input"
                  placeholder="e.g., Father, Sister, Friend"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">Police Station</label>
                <input
                  type="text"
                  name="police_station"
                  value={formData.police_station}
                  onChange={handleChange}
                  className="input"
                  placeholder="Where complaint was filed"
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
                  placeholder="If available"
                />
              </div>
            </div>

            <div>
              <label className="label">Additional Information</label>
              <textarea
                name="additional_info"
                value={formData.additional_info}
                onChange={handleChange}
                className="input min-h-[100px]"
                placeholder="Any other relevant details..."
              />
            </div>
          </div>
        </div>

        {}
        <div className="flex justify-end gap-4">
          <Link href="/missing-persons" className="btn-secondary">
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
                Create Report
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
