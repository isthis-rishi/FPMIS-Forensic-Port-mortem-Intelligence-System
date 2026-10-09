'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { casesApi, evidenceApi, todApi, decompositionApi, missingPersonsApi } from '@/lib/api';
import { Case, DeceasedInfo, AutopsyReport, Evidence, TODEstimation, DecompositionLog, MatchResult } from '@/types';
import { formatDate, formatDateTime, getStatusColor, getPriorityColor, getMannerOfDeathColor } from '@/lib/utils';
import {
  ArrowLeft, User, FileText, Clock, Package, Skull, Search, AlertTriangle,
  Plus, Save, CheckCircle, XCircle, Thermometer, Activity, Edit, Trash2
} from 'lucide-react';

type TabType = 'overview' | 'autopsy' | 'tod' | 'decomposition' | 'evidence' | 'matching';

export default function CaseDetailPage() {
  const params = useParams();
  const router = useRouter();
  const caseId = params.id as string;

  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [caseData, setCaseData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchCaseData();
  }, [caseId]);

  const fetchCaseData = async () => {
    setIsLoading(true);
    try {
      const data = await casesApi.get(caseId);
      setCaseData(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load case');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
        <p className="text-red-600">{error}</p>
        <Link href="/cases" className="text-primary-600 hover:underline mt-4 inline-block">
          Back to Cases
        </Link>
      </div>
    );
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: FileText },
    { id: 'autopsy', label: 'Autopsy', icon: Skull },
    { id: 'tod', label: 'Time of Death', icon: Clock },
    { id: 'decomposition', label: 'Decomposition', icon: Activity },
    { id: 'evidence', label: 'Evidence', icon: Package },
    { id: 'matching', label: 'Body Matching', icon: Search },
  ];

  return (
    <div>
      {}
      <div className="flex items-center gap-4 mb-6">
        <Link href="/cases" className="p-2 hover:bg-gray-100 rounded-lg">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-gray-900">{caseData.case_number}</h1>
            <span className={`badge ${getStatusColor(caseData.status)}`}>
              {caseData.status.replace('_', ' ')}
            </span>
            <span className={`badge ${getPriorityColor(caseData.priority)}`}>
              {caseData.priority}
            </span>
          </div>
          <p className="text-gray-600">
            {caseData.case_type?.replace('_', ' ')} • Created {formatDate(caseData.created_at)}
          </p>
        </div>
      </div>

      {}
      <div className="border-b border-gray-200 mb-6">
        <nav className="flex gap-4">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as TabType)}
              className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {}
      {activeTab === 'overview' && <OverviewTab caseData={caseData} onUpdate={fetchCaseData} />}
      {activeTab === 'autopsy' && <AutopsyTab caseId={caseId} onUpdate={fetchCaseData} />}
      {activeTab === 'tod' && <TODTab caseId={caseId} />}
      {activeTab === 'decomposition' && <DecompositionTab caseId={caseId} />}
      {activeTab === 'evidence' && <EvidenceTab caseId={caseId} />}
      {activeTab === 'matching' && <MatchingTab caseId={caseId} caseData={caseData} />}
    </div>
  );
}

function OverviewTab({ caseData, onUpdate }: { caseData: any; onUpdate: () => void }) {
  const deceased = caseData.deceased_info;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {}
      <div className="card">
        <div className="card-header">
          <h2 className="font-semibold">Case Information</h2>
        </div>
        <div className="card-body space-y-3">
          <InfoRow label="Case Number" value={caseData.case_number} />
          <InfoRow label="Case Type" value={caseData.case_type?.replace('_', ' ')} />
          <InfoRow label="Police Station" value={caseData.police_station || '-'} />
          <InfoRow label="FIR Number" value={caseData.fir_number || '-'} />
          <InfoRow label="Brought By" value={caseData.brought_by || '-'} />
          <InfoRow label="Body Received" value={caseData.body_received_at ? formatDateTime(caseData.body_received_at) : '-'} />
        </div>
      </div>

      {}
      <div className="card">
        <div className="card-header flex justify-between items-center">
          <h2 className="font-semibold">Deceased Information</h2>
          {deceased?.is_identified ? (
            <span className="badge bg-green-100 text-green-800">Identified</span>
          ) : (
            <span className="badge bg-yellow-100 text-yellow-800">Unidentified</span>
          )}
        </div>
        <div className="card-body space-y-3">
          {deceased ? (
            <>
              <InfoRow label="Name" value={deceased.name || 'Unknown'} />
              <InfoRow label="Gender" value={deceased.gender || 'Unknown'} />
              <InfoRow label="Age" value={deceased.age_years ? `${deceased.age_years} years` : 'Unknown'} />
              <InfoRow label="Height" value={deceased.height_cm ? `${deceased.height_cm} cm` : '-'} />
              <InfoRow label="Weight" value={deceased.weight_kg ? `${deceased.weight_kg} kg` : '-'} />
              <InfoRow label="Build" value={deceased.build || '-'} />
              <InfoRow label="Complexion" value={deceased.complexion || '-'} />
              <InfoRow label="District" value={deceased.district || '-'} />
              {deceased.identification_marks && (
                <div>
                  <p className="text-sm text-gray-500">Identification Marks</p>
                  <p className="text-gray-900">{deceased.identification_marks}</p>
                </div>
              )}
            </>
          ) : (
            <p className="text-gray-500">No deceased information recorded</p>
          )}
        </div>
      </div>

      {}
      <div className="card lg:col-span-2">
        <div className="card-header">
          <h2 className="font-semibold">Case Progress</h2>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatBox
              icon={Skull}
              label="Autopsy"
              value={caseData.autopsy_report ? (caseData.autopsy_report.is_finalized ? 'Finalized' : 'In Progress') : 'Pending'}
              color={caseData.autopsy_report?.is_finalized ? 'green' : 'yellow'}
            />
            <StatBox
              icon={Clock}
              label="TOD Estimated"
              value={caseData.tod_estimation ? 'Yes' : 'Pending'}
              color={caseData.tod_estimation ? 'green' : 'gray'}
            />
            <StatBox
              icon={Package}
              label="Evidence Items"
              value={caseData.evidence_count || '0'}
              color="blue"
            />
            <StatBox
              icon={Search}
              label="Match Status"
              value={deceased?.is_identified ? 'Identified' : 'Searching'}
              color={deceased?.is_identified ? 'green' : 'yellow'}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

function AutopsyTab({ caseId, onUpdate }: { caseId: string; onUpdate: () => void }) {
  const [autopsy, setAutopsy] = useState<AutopsyReport | null>(null);
  const [injuries, setInjuries] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [showInjuryForm, setShowInjuryForm] = useState(false);

  const [formData, setFormData] = useState({
    cause_of_death_immediate: '',
    cause_of_death_antecedent: '',
    cause_of_death_underlying: '',
    manner_of_death: 'pending',
    external_examination: '',
    internal_examination: '',
    doctors_remarks: '',
  });

  const [injuryForm, setInjuryForm] = useState({
    injury_type: 'laceration',
    body_region: 'head',
    body_side: 'central',
    length_cm: '',
    width_cm: '',
    depth_cm: '',
    description: '',
    probable_weapon: '',
    is_fatal: false,
  });

  useEffect(() => {
    fetchAutopsyData();
  }, [caseId]);

  const fetchAutopsyData = async () => {
    setIsLoading(true);
    try {
      const [autopsyRes, injuriesRes] = await Promise.all([
        casesApi.getAutopsy(caseId).catch(() => null),
        casesApi.getInjuries(caseId).catch(() => []),
      ]);
      setAutopsy(autopsyRes);
      setInjuries(injuriesRes || []);
      if (autopsyRes) {
        setFormData({
          cause_of_death_immediate: autopsyRes.cause_of_death_immediate || '',
          cause_of_death_antecedent: autopsyRes.cause_of_death_antecedent || '',
          cause_of_death_underlying: autopsyRes.cause_of_death_underlying || '',
          manner_of_death: autopsyRes.manner_of_death || 'pending',
          external_examination: autopsyRes.external_examination || '',
          internal_examination: autopsyRes.internal_examination || '',
          doctors_remarks: autopsyRes.doctors_remarks || '',
        });
      }
    } catch (err) {
      console.error('Failed to fetch autopsy:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveAutopsy = async () => {
    setIsSaving(true);
    try {
      if (autopsy) {
        await casesApi.updateAutopsy(caseId, formData);
      } else {
        await casesApi.createAutopsy(caseId, formData);
      }
      await fetchAutopsyData();
      setIsEditing(false);
      onUpdate();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to save autopsy');
    } finally {
      setIsSaving(false);
    }
  };

  const handleFinalizeAutopsy = async () => {
    if (!confirm('Are you sure you want to finalize? This cannot be undone.')) return;
    try {
      await casesApi.finalizeAutopsy(caseId);
      await fetchAutopsyData();
      onUpdate();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to finalize');
    }
  };

  const handleAddInjury = async () => {
    try {
      await casesApi.addInjury(caseId, {
        ...injuryForm,
        length_cm: injuryForm.length_cm ? parseFloat(injuryForm.length_cm) : undefined,
        width_cm: injuryForm.width_cm ? parseFloat(injuryForm.width_cm) : undefined,
        depth_cm: injuryForm.depth_cm ? parseFloat(injuryForm.depth_cm) : undefined,
      });
      setShowInjuryForm(false);
      setInjuryForm({
        injury_type: 'laceration',
        body_region: 'head',
        body_side: 'central',
        length_cm: '',
        width_cm: '',
        depth_cm: '',
        description: '',
        probable_weapon: '',
        is_fatal: false,
      });
      await fetchAutopsyData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to add injury');
    }
  };

  const handleDeleteInjury = async (injuryId: string) => {
    if (!confirm('Delete this injury record?')) return;
    try {
      await casesApi.deleteInjury(caseId, injuryId);
      await fetchAutopsyData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete');
    }
  };

  if (isLoading) {
    return <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div></div>;
  }

  const isFinalized = autopsy?.is_finalized;

  return (
    <div className="space-y-6">
      {}
      <div className="card">
        <div className="card-header flex justify-between items-center">
          <h2 className="font-semibold">Autopsy Report</h2>
          <div className="flex gap-2">
            {isFinalized ? (
              <span className="badge bg-green-100 text-green-800">Finalized</span>
            ) : (
              <>
                {!isEditing && (
                  <button onClick={() => setIsEditing(true)} className="btn-secondary text-sm py-1">
                    <Edit className="w-4 h-4 mr-1" /> Edit
                  </button>
                )}
                {autopsy && !isEditing && (
                  <button onClick={handleFinalizeAutopsy} className="btn-success text-sm py-1">
                    <CheckCircle className="w-4 h-4 mr-1" /> Finalize
                  </button>
                )}
              </>
            )}
          </div>
        </div>
        <div className="card-body">
          {isEditing ? (
            <div className="space-y-4">
              <div>
                <label className="label">Immediate Cause of Death</label>
                <input
                  type="text"
                  value={formData.cause_of_death_immediate}
                  onChange={(e) => setFormData({ ...formData, cause_of_death_immediate: e.target.value })}
                  className="input"
                  placeholder="Direct cause of death"
                />
              </div>
              <div>
                <label className="label">Antecedent Cause</label>
                <input
                  type="text"
                  value={formData.cause_of_death_antecedent}
                  onChange={(e) => setFormData({ ...formData, cause_of_death_antecedent: e.target.value })}
                  className="input"
                  placeholder="Condition leading to immediate cause"
                />
              </div>
              <div>
                <label className="label">Underlying Cause</label>
                <input
                  type="text"
                  value={formData.cause_of_death_underlying}
                  onChange={(e) => setFormData({ ...formData, cause_of_death_underlying: e.target.value })}
                  className="input"
                  placeholder="Root cause"
                />
              </div>
              <div>
                <label className="label">Manner of Death</label>
                <select
                  value={formData.manner_of_death}
                  onChange={(e) => setFormData({ ...formData, manner_of_death: e.target.value })}
                  className="input"
                >
                  <option value="pending">Pending Investigation</option>
                  <option value="natural">Natural</option>
                  <option value="accident">Accident</option>
                  <option value="suicide">Suicide</option>
                  <option value="homicide">Homicide</option>
                  <option value="undetermined">Undetermined</option>
                </select>
              </div>
              <div>
                <label className="label">External Examination</label>
                <textarea
                  value={formData.external_examination}
                  onChange={(e) => setFormData({ ...formData, external_examination: e.target.value })}
                  className="input min-h-[100px]"
                  placeholder="External body examination findings..."
                />
              </div>
              <div>
                <label className="label">Internal Examination</label>
                <textarea
                  value={formData.internal_examination}
                  onChange={(e) => setFormData({ ...formData, internal_examination: e.target.value })}
                  className="input min-h-[100px]"
                  placeholder="Internal organ examination findings..."
                />
              </div>
              <div>
                <label className="label">Doctor&apos;s Remarks</label>
                <textarea
                  value={formData.doctors_remarks}
                  onChange={(e) => setFormData({ ...formData, doctors_remarks: e.target.value })}
                  className="input min-h-[80px]"
                  placeholder="Additional remarks and observations..."
                />
              </div>
              <div className="flex gap-2">
                <button onClick={handleSaveAutopsy} disabled={isSaving} className="btn-primary">
                  {isSaving ? 'Saving...' : 'Save Report'}
                </button>
                <button onClick={() => setIsEditing(false)} className="btn-secondary">Cancel</button>
              </div>
            </div>
          ) : autopsy ? (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <InfoRow label="Immediate Cause" value={autopsy.cause_of_death_immediate || '-'} />
                <InfoRow label="Antecedent Cause" value={autopsy.cause_of_death_antecedent || '-'} />
                <InfoRow label="Underlying Cause" value={autopsy.cause_of_death_underlying || '-'} />
                <div>
                  <p className="text-sm text-gray-500">Manner of Death</p>
                  <span className={`badge ${getMannerOfDeathColor(autopsy.manner_of_death || 'pending')}`}>
                    {autopsy.manner_of_death || 'Pending'}
                  </span>
                </div>
              </div>
              {autopsy.external_examination && (
                <div>
                  <p className="text-sm text-gray-500 mb-1">External Examination</p>
                  <p className="text-gray-900 whitespace-pre-wrap">{autopsy.external_examination}</p>
                </div>
              )}
              {autopsy.internal_examination && (
                <div>
                  <p className="text-sm text-gray-500 mb-1">Internal Examination</p>
                  <p className="text-gray-900 whitespace-pre-wrap">{autopsy.internal_examination}</p>
                </div>
              )}
              {autopsy.doctors_remarks && (
                <div>
                  <p className="text-sm text-gray-500 mb-1">Doctor&apos;s Remarks</p>
                  <p className="text-gray-900 whitespace-pre-wrap">{autopsy.doctors_remarks}</p>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-8">
              <Skull className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500 mb-4">No autopsy report started</p>
              <button onClick={() => setIsEditing(true)} className="btn-primary">
                Start Autopsy Report
              </button>
            </div>
          )}
        </div>
      </div>

      {}
      <div className="card">
        <div className="card-header flex justify-between items-center">
          <h2 className="font-semibold">Injuries ({injuries.length})</h2>
          {!isFinalized && (
            <button onClick={() => setShowInjuryForm(true)} className="btn-secondary text-sm py-1">
              <Plus className="w-4 h-4 mr-1" /> Add Injury
            </button>
          )}
        </div>
        <div className="card-body">
          {showInjuryForm && (
            <div className="mb-6 p-4 bg-gray-50 rounded-lg space-y-4">
              <h3 className="font-medium">Add New Injury</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <label className="label">Type</label>
                  <select
                    value={injuryForm.injury_type}
                    onChange={(e) => setInjuryForm({ ...injuryForm, injury_type: e.target.value })}
                    className="input"
                  >
                    <option value="laceration">Laceration</option>
                    <option value="abrasion">Abrasion</option>
                    <option value="contusion">Contusion</option>
                    <option value="incised_wound">Incised Wound</option>
                    <option value="stab_wound">Stab Wound</option>
                    <option value="gunshot_wound">Gunshot Wound</option>
                    <option value="burn">Burn</option>
                    <option value="fracture">Fracture</option>
                    <option value="other">Other</option>
                  </select>
                </div>
                <div>
                  <label className="label">Body Region</label>
                  <select
                    value={injuryForm.body_region}
                    onChange={(e) => setInjuryForm({ ...injuryForm, body_region: e.target.value })}
                    className="input"
                  >
                    <option value="head">Head</option>
                    <option value="face">Face</option>
                    <option value="neck">Neck</option>
                    <option value="chest">Chest</option>
                    <option value="abdomen">Abdomen</option>
                    <option value="back">Back</option>
                    <option value="upper_limb">Upper Limb</option>
                    <option value="lower_limb">Lower Limb</option>
                    <option value="genitals">Genitals</option>
                  </select>
                </div>
                <div>
                  <label className="label">Side</label>
                  <select
                    value={injuryForm.body_side}
                    onChange={(e) => setInjuryForm({ ...injuryForm, body_side: e.target.value })}
                    className="input"
                  >
                    <option value="left">Left</option>
                    <option value="right">Right</option>
                    <option value="central">Central</option>
                    <option value="bilateral">Bilateral</option>
                  </select>
                </div>
                <div className="flex items-end">
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={injuryForm.is_fatal}
                      onChange={(e) => setInjuryForm({ ...injuryForm, is_fatal: e.target.checked })}
                      className="w-4 h-4"
                    />
                    <span className="text-sm">Fatal Injury</span>
                  </label>
                </div>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="label">Length (cm)</label>
                  <input
                    type="number"
                    value={injuryForm.length_cm}
                    onChange={(e) => setInjuryForm({ ...injuryForm, length_cm: e.target.value })}
                    className="input"
                    step="0.1"
                  />
                </div>
                <div>
                  <label className="label">Width (cm)</label>
                  <input
                    type="number"
                    value={injuryForm.width_cm}
                    onChange={(e) => setInjuryForm({ ...injuryForm, width_cm: e.target.value })}
                    className="input"
                    step="0.1"
                  />
                </div>
                <div>
                  <label className="label">Depth (cm)</label>
                  <input
                    type="number"
                    value={injuryForm.depth_cm}
                    onChange={(e) => setInjuryForm({ ...injuryForm, depth_cm: e.target.value })}
                    className="input"
                    step="0.1"
                  />
                </div>
              </div>
              <div>
                <label className="label">Description</label>
                <textarea
                  value={injuryForm.description}
                  onChange={(e) => setInjuryForm({ ...injuryForm, description: e.target.value })}
                  className="input"
                  placeholder="Detailed description of the injury..."
                />
              </div>
              <div>
                <label className="label">Probable Weapon/Cause</label>
                <input
                  type="text"
                  value={injuryForm.probable_weapon}
                  onChange={(e) => setInjuryForm({ ...injuryForm, probable_weapon: e.target.value })}
                  className="input"
                  placeholder="e.g., Blunt object, Sharp knife, Fall from height"
                />
              </div>
              <div className="flex gap-2">
                <button onClick={handleAddInjury} className="btn-primary">Add Injury</button>
                <button onClick={() => setShowInjuryForm(false)} className="btn-secondary">Cancel</button>
              </div>
            </div>
          )}

          {injuries.length === 0 ? (
            <p className="text-gray-500 text-center py-4">No injuries recorded</p>
          ) : (
            <div className="space-y-3">
              {injuries.map((injury, index) => (
                <div key={injury.id} className="flex items-start justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-medium capitalize">{injury.injury_type.replace('_', ' ')}</span>
                      <span className="text-sm text-gray-500">
                        {injury.body_region} ({injury.body_side})
                      </span>
                      {injury.is_fatal && (
                        <span className="badge bg-red-100 text-red-800">Fatal</span>
                      )}
                    </div>
                    {injury.description && <p className="text-sm text-gray-600 mt-1">{injury.description}</p>}
                    <div className="text-xs text-gray-500 mt-1">
                      {injury.length_cm && `${injury.length_cm}cm × `}
                      {injury.width_cm && `${injury.width_cm}cm`}
                      {injury.depth_cm && ` × ${injury.depth_cm}cm deep`}
                      {injury.probable_weapon && ` • ${injury.probable_weapon}`}
                    </div>
                  </div>
                  {!isFinalized && (
                    <button
                      onClick={() => handleDeleteInjury(injury.id)}
                      className="text-red-500 hover:text-red-700 p-1"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function TODTab({ caseId }: { caseId: string }) {
  const [todData, setTodData] = useState<TODEstimation | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isCalculating, setIsCalculating] = useState(false);
  const [showForm, setShowForm] = useState(false);

  const [formData, setFormData] = useState({
    body_temperature_celsius: '',
    ambient_temperature_celsius: '25',
    body_weight_kg: '70',
    environment: 'indoor',
    rigor_mortis_jaw: '0',
    rigor_mortis_neck: '0',
    rigor_mortis_upper_limbs: '0',
    rigor_mortis_lower_limbs: '0',
    livor_mortis_present: false,
    livor_mortis_fixed: false,
    corneal_opacity: '0',
    decomposition_stage: 'fresh',
  });

  useEffect(() => {
    fetchTOD();
  }, [caseId]);

  const fetchTOD = async () => {
    setIsLoading(true);
    try {
      const data = await todApi.get(caseId);
      setTodData(data);
    } catch (err) {
      setTodData(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCalculate = async () => {
    setIsCalculating(true);
    try {
      const payload = {
        body_temperature_celsius: formData.body_temperature_celsius ? parseFloat(formData.body_temperature_celsius) : undefined,
        ambient_temperature_celsius: parseFloat(formData.ambient_temperature_celsius),
        body_weight_kg: parseFloat(formData.body_weight_kg),
        environment: formData.environment,
        rigor_mortis_jaw: parseInt(formData.rigor_mortis_jaw),
        rigor_mortis_neck: parseInt(formData.rigor_mortis_neck),
        rigor_mortis_upper_limbs: parseInt(formData.rigor_mortis_upper_limbs),
        rigor_mortis_lower_limbs: parseInt(formData.rigor_mortis_lower_limbs),
        livor_mortis_present: formData.livor_mortis_present,
        livor_mortis_fixed: formData.livor_mortis_fixed,
        corneal_opacity: parseInt(formData.corneal_opacity),
        decomposition_stage: formData.decomposition_stage,
      };
      await todApi.calculate(caseId, payload);
      await fetchTOD();
      setShowForm(false);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Calculation failed');
    } finally {
      setIsCalculating(false);
    }
  };

  if (isLoading) {
    return <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div></div>;
  }

  const rigorOptions = [
    { value: '0', label: '0 - Absent' },
    { value: '1', label: '1 - Developing' },
    { value: '2', label: '2 - Moderate' },
    { value: '3', label: '3 - Full' },
    { value: '4', label: '4 - Passing' },
  ];

  return (
    <div className="space-y-6">
      {}
      {todData && (
        <div className="card">
          <div className="card-header">
            <h2 className="font-semibold">Current Estimation</h2>
          </div>
          <div className="card-body">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center p-6 bg-primary-50 rounded-xl">
                <Clock className="w-12 h-12 text-primary-600 mx-auto mb-2" />
                <p className="text-3xl font-bold text-primary-600">
                  {Number(todData.estimated_tod_min_hours || 0).toFixed(1)} - {Number(todData.estimated_tod_max_hours || 0).toFixed(1)}
                </p>
                <p className="text-gray-600">Hours Since Death</p>
              </div>
              <div className="text-center p-6 bg-gray-50 rounded-xl">
                <p className="text-sm text-gray-500 mb-1">Confidence Level</p>
                <p className={`text-2xl font-bold capitalize ${
                  todData.confidence_level === 'high' ? 'text-green-600' :
                  todData.confidence_level === 'medium' ? 'text-yellow-600' : 'text-red-600'
                }`}>
                  {todData.confidence_level || 'N/A'}
                </p>
              </div>
              <div className="text-center p-6 bg-gray-50 rounded-xl">
                <p className="text-sm text-gray-500 mb-1">Estimated Time of Death</p>
                <p className="text-lg font-medium">
                  {todData.estimated_datetime_min ? formatDateTime(todData.estimated_datetime_min) : '-'}
                </p>
              </div>
            </div>
            {todData.calculation_reasoning && (
              <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-500 mb-1">Calculation Reasoning</p>
                <p className="text-gray-700">{todData.calculation_reasoning}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {}
      <div className="card">
        <div className="card-header flex justify-between items-center">
          <h2 className="font-semibold">TOD Calculator</h2>
          {!showForm && (
            <button onClick={() => setShowForm(true)} className="btn-primary text-sm">
              {todData ? 'Recalculate' : 'Calculate TOD'}
            </button>
          )}
        </div>
        {showForm && (
          <div className="card-body space-y-6">
            {}
            <div>
              <h3 className="font-medium mb-3 flex items-center gap-2">
                <Thermometer className="w-5 h-5" /> Temperature Readings
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="label">Body Temperature (°C)</label>
                  <input
                    type="number"
                    value={formData.body_temperature_celsius}
                    onChange={(e) => setFormData({ ...formData, body_temperature_celsius: e.target.value })}
                    className="input"
                    placeholder="e.g., 32"
                    step="0.1"
                  />
                  <p className="text-xs text-gray-500 mt-1">Normal: 37°C</p>
                </div>
                <div>
                  <label className="label">Ambient Temperature (°C)</label>
                  <input
                    type="number"
                    value={formData.ambient_temperature_celsius}
                    onChange={(e) => setFormData({ ...formData, ambient_temperature_celsius: e.target.value })}
                    className="input"
                    step="0.1"
                  />
                </div>
                <div>
                  <label className="label">Body Weight (kg)</label>
                  <input
                    type="number"
                    value={formData.body_weight_kg}
                    onChange={(e) => setFormData({ ...formData, body_weight_kg: e.target.value })}
                    className="input"
                  />
                </div>
              </div>
            </div>

            {}
            <div>
              <label className="label">Environment</label>
              <select
                value={formData.environment}
                onChange={(e) => setFormData({ ...formData, environment: e.target.value })}
                className="input w-auto"
              >
                <option value="indoor">Indoor</option>
                <option value="outdoor">Outdoor</option>
                <option value="water">Water</option>
                <option value="buried">Buried</option>
              </select>
            </div>

            {}
            <div>
              <h3 className="font-medium mb-3">Rigor Mortis (0-4 Scale)</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <label className="label">Jaw</label>
                  <select
                    value={formData.rigor_mortis_jaw}
                    onChange={(e) => setFormData({ ...formData, rigor_mortis_jaw: e.target.value })}
                    className="input"
                  >
                    {rigorOptions.map(opt => (
                      <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="label">Neck</label>
                  <select
                    value={formData.rigor_mortis_neck}
                    onChange={(e) => setFormData({ ...formData, rigor_mortis_neck: e.target.value })}
                    className="input"
                  >
                    {rigorOptions.map(opt => (
                      <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="label">Upper Limbs</label>
                  <select
                    value={formData.rigor_mortis_upper_limbs}
                    onChange={(e) => setFormData({ ...formData, rigor_mortis_upper_limbs: e.target.value })}
                    className="input"
                  >
                    {rigorOptions.map(opt => (
                      <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="label">Lower Limbs</label>
                  <select
                    value={formData.rigor_mortis_lower_limbs}
                    onChange={(e) => setFormData({ ...formData, rigor_mortis_lower_limbs: e.target.value })}
                    className="input"
                  >
                    {rigorOptions.map(opt => (
                      <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            {}
            <div>
              <h3 className="font-medium mb-3">Livor Mortis</h3>
              <div className="flex gap-6">
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={formData.livor_mortis_present}
                    onChange={(e) => setFormData({ ...formData, livor_mortis_present: e.target.checked })}
                    className="w-4 h-4"
                  />
                  <span>Present</span>
                </label>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={formData.livor_mortis_fixed}
                    onChange={(e) => setFormData({ ...formData, livor_mortis_fixed: e.target.checked })}
                    className="w-4 h-4"
                    disabled={!formData.livor_mortis_present}
                  />
                  <span>Fixed (Non-blanching)</span>
                </label>
              </div>
            </div>

            {}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">Corneal Opacity (0-4)</label>
                <select
                  value={formData.corneal_opacity}
                  onChange={(e) => setFormData({ ...formData, corneal_opacity: e.target.value })}
                  className="input"
                >
                  <option value="0">0 - Clear</option>
                  <option value="1">1 - Slight haze</option>
                  <option value="2">2 - Moderate opacity</option>
                  <option value="3">3 - Marked opacity</option>
                  <option value="4">4 - Complete opacity</option>
                </select>
              </div>
              <div>
                <label className="label">Decomposition Stage</label>
                <select
                  value={formData.decomposition_stage}
                  onChange={(e) => setFormData({ ...formData, decomposition_stage: e.target.value })}
                  className="input"
                >
                  <option value="fresh">Fresh (0-2 days)</option>
                  <option value="early_decomposition">Early Decomposition (2-6 days)</option>
                  <option value="bloat">Bloat (4-10 days)</option>
                  <option value="active_decay">Active Decay (10-25 days)</option>
                  <option value="advanced_decay">Advanced Decay (25+ days)</option>
                </select>
              </div>
            </div>

            {}
            <div className="flex gap-2 pt-4 border-t">
              <button
                onClick={handleCalculate}
                disabled={isCalculating}
                className="btn-primary flex items-center gap-2"
              >
                {isCalculating ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    Calculating...
                  </>
                ) : (
                  <>
                    <Clock className="w-4 h-4" />
                    Calculate Time of Death
                  </>
                )}
              </button>
              <button onClick={() => setShowForm(false)} className="btn-secondary">Cancel</button>
            </div>
          </div>
        )}
        {!showForm && !todData && (
          <div className="card-body text-center py-12">
            <Clock className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 mb-4">No time of death estimation yet</p>
            <button onClick={() => setShowForm(true)} className="btn-primary">
              Calculate TOD
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

function DecompositionTab({ caseId }: { caseId: string }) {
  const [logs, setLogs] = useState<DecompositionLog[]>([]);
  const [stages, setStages] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const [formData, setFormData] = useState({
    stage: 'fresh',
    temperature_celsius: '',
    humidity_percent: '',
    weather_conditions: '',
    location_type: 'indoor',
    sun_exposure: 'none',
    insect_activity_present: false,
    insect_types: '',
    maggot_stage: '',
    maggot_mass_present: false,
    skin_changes: '',
    bloating_level: '0',
    purging_present: false,
    marbling_present: false,
    observations: '',
  });

  useEffect(() => {
    fetchData();
  }, [caseId]);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const [logsData, stagesData] = await Promise.all([
        decompositionApi.list(caseId).catch(() => []),
        decompositionApi.getStages(caseId).catch(() => []),
      ]);
      setLogs(logsData || []);
      setStages(stagesData || []);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async () => {
    setIsSaving(true);
    try {
      await decompositionApi.log(caseId, {
        stage: formData.stage,
        temperature_celsius: formData.temperature_celsius ? parseFloat(formData.temperature_celsius) : undefined,
        humidity_percent: formData.humidity_percent ? parseFloat(formData.humidity_percent) : undefined,
        weather_condition: formData.weather_conditions || undefined,
        location_type: formData.location_type || undefined,
        sun_exposure: formData.sun_exposure || undefined,
        insect_activity_present: formData.insect_activity_present || undefined,
        insect_types: formData.insect_types || undefined,
        maggot_stage: formData.maggot_stage || undefined,
        maggot_mass_present: formData.maggot_mass_present || undefined,
        skin_changes: formData.skin_changes || undefined,
        bloating_level: formData.bloating_level || undefined,
        purging_present: formData.purging_present || undefined,
        marbling_present: formData.marbling_present || undefined,
        additional_observations: formData.observations || undefined,
      });
      await fetchData();
      setShowForm(false);
      setFormData({
        stage: 'fresh',
        temperature_celsius: '',
        humidity_percent: '',
        weather_conditions: '',
        location_type: 'indoor',
        sun_exposure: 'none',
        insect_activity_present: false,
        insect_types: '',
        maggot_stage: '',
        maggot_mass_present: false,
        skin_changes: '',
        bloating_level: '0',
        purging_present: false,
        marbling_present: false,
        observations: '',
      });
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to save');
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div></div>;
  }

  const stageColors: Record<string, string> = {
    fresh: 'bg-green-100 text-green-800',
    early_decomposition: 'bg-yellow-100 text-yellow-800',
    bloat: 'bg-orange-100 text-orange-800',
    active_decay: 'bg-red-100 text-red-800',
    advanced_decay: 'bg-purple-100 text-purple-800',
    dry_remains: 'bg-gray-100 text-gray-800',
    skeletonization: 'bg-gray-200 text-gray-900',
  };

  return (
    <div className="space-y-6">
      {}
      {stages.length > 0 && (
        <div className="card">
          <div className="card-header">
            <h2 className="font-semibold">Decomposition Stages Reference</h2>
          </div>
          <div className="card-body">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
              {stages.map((stage: any) => (
                <div key={stage.stage} className="p-3 bg-gray-50 rounded-lg">
                  <span className={`badge ${stageColors[stage.stage] || 'bg-gray-100'} mb-1`}>
                    {stage.stage.replace('_', ' ')}
                  </span>
                  <p className="text-xs text-gray-600">{stage.typical_timeframe}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {}
      <div className="card">
        <div className="card-header flex justify-between items-center">
          <h2 className="font-semibold">Decomposition Logs ({logs.length})</h2>
          {!showForm && (
            <button onClick={() => setShowForm(true)} className="btn-primary text-sm">
              <Plus className="w-4 h-4 mr-1" /> Add Log
            </button>
          )}
        </div>
        {showForm && (
          <div className="card-body space-y-4 border-b">
            <h3 className="font-medium">New Decomposition Log</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="label">Stage</label>
                <select
                  value={formData.stage}
                  onChange={(e) => setFormData({ ...formData, stage: e.target.value })}
                  className="input"
                >
                  <option value="fresh">Fresh</option>
                  <option value="early_decomposition">Early Decomposition</option>
                  <option value="bloat">Bloat</option>
                  <option value="active_decay">Active Decay</option>
                  <option value="advanced_decay">Advanced Decay</option>
                  <option value="dry_remains">Dry Remains</option>
                  <option value="skeletonization">Skeletonization</option>
                </select>
              </div>
              <div>
                <label className="label">Temperature (°C)</label>
                <input
                  type="number"
                  value={formData.temperature_celsius}
                  onChange={(e) => setFormData({ ...formData, temperature_celsius: e.target.value })}
                  className="input"
                  step="0.1"
                />
              </div>
              <div>
                <label className="label">Humidity (%)</label>
                <input
                  type="number"
                  value={formData.humidity_percent}
                  onChange={(e) => setFormData({ ...formData, humidity_percent: e.target.value })}
                  className="input"
                  min="0"
                  max="100"
                />
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="label">Location Type</label>
                <select
                  value={formData.location_type}
                  onChange={(e) => setFormData({ ...formData, location_type: e.target.value })}
                  className="input"
                >
                  <option value="indoor">Indoor</option>
                  <option value="outdoor">Outdoor</option>
                  <option value="water">Water</option>
                  <option value="buried">Buried</option>
                  <option value="vehicle">Vehicle</option>
                </select>
              </div>
              <div>
                <label className="label">Sun Exposure</label>
                <select
                  value={formData.sun_exposure}
                  onChange={(e) => setFormData({ ...formData, sun_exposure: e.target.value })}
                  className="input"
                >
                  <option value="none">None</option>
                  <option value="partial">Partial</option>
                  <option value="full">Full</option>
                </select>
              </div>
              <div>
                <label className="label">Weather</label>
                <input
                  type="text"
                  value={formData.weather_conditions}
                  onChange={(e) => setFormData({ ...formData, weather_conditions: e.target.value })}
                  className="input"
                  placeholder="e.g., Hot and humid"
                />
              </div>
            </div>

            {}
            <div className="p-4 bg-gray-50 rounded-lg space-y-3">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={formData.insect_activity_present}
                  onChange={(e) => setFormData({ ...formData, insect_activity_present: e.target.checked })}
                  className="w-4 h-4"
                />
                <span className="font-medium">Insect Activity Present</span>
              </label>
              {formData.insect_activity_present && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pl-6">
                  <div>
                    <label className="label">Insect Types</label>
                    <input
                      type="text"
                      value={formData.insect_types}
                      onChange={(e) => setFormData({ ...formData, insect_types: e.target.value })}
                      className="input"
                      placeholder="Flies, beetles..."
                    />
                  </div>
                  <div>
                    <label className="label">Maggot Stage</label>
                    <select
                      value={formData.maggot_stage}
                      onChange={(e) => setFormData({ ...formData, maggot_stage: e.target.value })}
                      className="input"
                    >
                      <option value="">None</option>
                      <option value="eggs">Eggs</option>
                      <option value="first_instar">First Instar</option>
                      <option value="second_instar">Second Instar</option>
                      <option value="third_instar">Third Instar</option>
                      <option value="pupae">Pupae</option>
                    </select>
                  </div>
                  <div className="flex items-end">
                    <label className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={formData.maggot_mass_present}
                        onChange={(e) => setFormData({ ...formData, maggot_mass_present: e.target.checked })}
                        className="w-4 h-4"
                      />
                      <span>Maggot Mass Present</span>
                    </label>
                  </div>
                </div>
              )}
            </div>

            {}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <label className="label">Bloating Level (0-4)</label>
                <select
                  value={formData.bloating_level}
                  onChange={(e) => setFormData({ ...formData, bloating_level: e.target.value })}
                  className="input"
                >
                  <option value="0">0 - None</option>
                  <option value="1">1 - Slight</option>
                  <option value="2">2 - Moderate</option>
                  <option value="3">3 - Severe</option>
                  <option value="4">4 - Extreme</option>
                </select>
              </div>
              <label className="flex items-end gap-2 pb-2">
                <input
                  type="checkbox"
                  checked={formData.purging_present}
                  onChange={(e) => setFormData({ ...formData, purging_present: e.target.checked })}
                  className="w-4 h-4"
                />
                <span>Purging Present</span>
              </label>
              <label className="flex items-end gap-2 pb-2">
                <input
                  type="checkbox"
                  checked={formData.marbling_present}
                  onChange={(e) => setFormData({ ...formData, marbling_present: e.target.checked })}
                  className="w-4 h-4"
                />
                <span>Marbling Present</span>
              </label>
            </div>

            <div>
              <label className="label">Observations</label>
              <textarea
                value={formData.observations}
                onChange={(e) => setFormData({ ...formData, observations: e.target.value })}
                className="input min-h-[80px]"
                placeholder="Additional observations..."
              />
            </div>

            <div className="flex gap-2">
              <button onClick={handleSubmit} disabled={isSaving} className="btn-primary">
                {isSaving ? 'Saving...' : 'Save Log'}
              </button>
              <button onClick={() => setShowForm(false)} className="btn-secondary">Cancel</button>
            </div>
          </div>
        )}
        <div className="card-body">
          {logs.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No decomposition logs recorded</p>
          ) : (
            <div className="space-y-4">
              {logs.map((log: any) => (
                <div key={log.id} className="p-4 border rounded-lg">
                  <div className="flex items-start justify-between mb-2">
                    <span className={`badge ${stageColors[log.stage] || 'bg-gray-100'}`}>
                      {log.stage.replace('_', ' ')}
                    </span>
                    <span className="text-sm text-gray-500">{formatDateTime(log.logged_at)}</span>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
                    {log.temperature_celsius && <span>Temp: {log.temperature_celsius}°C</span>}
                    {log.humidity_percent && <span>Humidity: {log.humidity_percent}%</span>}
                    {log.location_type && <span>Location: {log.location_type}</span>}
                    {log.insect_activity_present && <span className="text-orange-600">🪰 Insect Activity</span>}
                  </div>
                  {log.observations && <p className="text-gray-600 mt-2">{log.observations}</p>}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function EvidenceTab({ caseId }: { caseId: string }) {
  const [evidence, setEvidence] = useState<Evidence[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [selectedEvidence, setSelectedEvidence] = useState<string | null>(null);
  const [chainHistory, setChainHistory] = useState<any[]>([]);

  const [formData, setFormData] = useState({
    evidence_number: '',
    item_type: 'biological_sample',
    item_name: '',
    description: '',
    quantity: '1',
    storage_location: '',
  });

  useEffect(() => {
    fetchEvidence();
  }, [caseId]);

  const fetchEvidence = async () => {
    setIsLoading(true);
    try {
      const data = await evidenceApi.list(caseId);
      setEvidence(data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddEvidence = async () => {
    if (!formData.evidence_number || !formData.item_name) {
      alert('Please fill in Evidence Number and Item Name');
      return;
    }
    try {
      await evidenceApi.create(caseId, {
        evidence_number: formData.evidence_number,
        item_type: formData.item_type,
        item_name: formData.item_name,
        description: formData.description || undefined,
        storage_location: formData.storage_location || undefined,
      });
      await fetchEvidence();
      setShowForm(false);
      setFormData({
        evidence_number: '',
        item_type: 'biological_sample',
        item_name: '',
        description: '',
        quantity: '1',
        storage_location: '',
      });
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to add evidence');
    }
  };

  const handleViewChain = async (evidenceId: string) => {
    try {
      const chain = await evidenceApi.getChain(evidenceId);
      setChainHistory(chain || []);
      setSelectedEvidence(evidenceId);
    } catch (err) {
      alert('Failed to load chain of custody');
    }
  };

  if (isLoading) {
    return <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div></div>;
  }

  const evidenceTypes = [
    'biological_sample', 'clothing', 'weapon', 'document', 'electronic',
    'toxicology_sample', 'dna_sample', 'photograph', 'personal_belongings', 'other'
  ];

  return (
    <div className="space-y-6">
      {}
      <div className="card">
        <div className="card-header flex justify-between items-center">
          <h2 className="font-semibold">Evidence Items ({evidence.length})</h2>
          {!showForm && (
            <button onClick={() => setShowForm(true)} className="btn-primary text-sm">
              <Plus className="w-4 h-4 mr-1" /> Add Evidence
            </button>
          )}
        </div>
        {showForm && (
          <div className="card-body border-b space-y-4">
            <h3 className="font-medium">Add New Evidence</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="label">Evidence Number *</label>
                <input
                  type="text"
                  value={formData.evidence_number}
                  onChange={(e) => setFormData({ ...formData, evidence_number: e.target.value })}
                  className="input"
                  placeholder="e.g., EVD-001"
                  required
                />
              </div>
              <div>
                <label className="label">Item Type</label>
                <select
                  value={formData.item_type}
                  onChange={(e) => setFormData({ ...formData, item_type: e.target.value })}
                  className="input"
                >
                  {evidenceTypes.map(type => (
                    <option key={type} value={type}>{type.replace('_', ' ')}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="label">Item Name *</label>
                <input
                  type="text"
                  value={formData.item_name}
                  onChange={(e) => setFormData({ ...formData, item_name: e.target.value })}
                  className="input"
                  placeholder="e.g., Blood sample from scene"
                  required
                />
              </div>
            </div>
            <div>
              <label className="label">Description</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="input"
                placeholder="Detailed description..."
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="label">Quantity</label>
                <input
                  type="number"
                  value={formData.quantity}
                  onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
                  className="input"
                  min="1"
                />
              </div>
              <div>
                <label className="label">Storage Location</label>
                <input
                  type="text"
                  value={formData.storage_location}
                  onChange={(e) => setFormData({ ...formData, storage_location: e.target.value })}
                  className="input"
                  placeholder="e.g., Evidence Room A-12"
                />
              </div>
            </div>
            <div className="flex gap-2">
              <button onClick={handleAddEvidence} className="btn-primary">Add Evidence</button>
              <button onClick={() => setShowForm(false)} className="btn-secondary">Cancel</button>
            </div>
          </div>
        )}
        <div className="card-body">
          {evidence.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No evidence items recorded</p>
          ) : (
            <div className="space-y-3">
              {evidence.map((item: any) => (
                <div key={item.id} className="p-4 border rounded-lg">
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <Package className="w-5 h-5 text-gray-400" />
                        <span className="font-medium">{item.item_name}</span>
                        <span className="text-sm text-gray-500">#{item.evidence_number}</span>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">{item.description}</p>
                      <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                        <span className="capitalize">{item.item_type.replace('_', ' ')}</span>
                        <span>Qty: {item.quantity}</span>
                        {item.current_location && <span>📍 {item.current_location}</span>}
                      </div>
                    </div>
                    <div className="flex flex-col items-end gap-2">
                      <span className={`badge ${getStatusColor(item.status)}`}>
                        {item.status.replace('_', ' ')}
                      </span>
                      <button
                        onClick={() => handleViewChain(item.id)}
                        className="text-xs text-primary-600 hover:underline"
                      >
                        View Chain of Custody
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {}
      {selectedEvidence && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-2xl w-full max-h-[80vh] overflow-auto">
            <div className="p-4 border-b flex justify-between items-center">
              <h3 className="font-semibold">Chain of Custody</h3>
              <button onClick={() => setSelectedEvidence(null)} className="text-gray-500 hover:text-gray-700">
                <XCircle className="w-5 h-5" />
              </button>
            </div>
            <div className="p-4">
              {chainHistory.length === 0 ? (
                <p className="text-gray-500 text-center py-4">No custody transfers recorded</p>
              ) : (
                <div className="space-y-4">
                  {chainHistory.map((entry: any, index: number) => (
                    <div key={entry.id} className="flex gap-4">
                      <div className="flex flex-col items-center">
                        <div className="w-3 h-3 bg-primary-600 rounded-full"></div>
                        {index < chainHistory.length - 1 && <div className="w-0.5 h-full bg-gray-200"></div>}
                      </div>
                      <div className="flex-1 pb-4">
                        <p className="font-medium capitalize">{entry.action_type.replace('_', ' ')}</p>
                        <p className="text-sm text-gray-600">
                          {entry.from_user_name && `From: ${entry.from_user_name}`}
                          {entry.to_user_name && ` → To: ${entry.to_user_name}`}
                        </p>
                        {entry.purpose && <p className="text-sm text-gray-500">{entry.purpose}</p>}
                        <p className="text-xs text-gray-400 mt-1">{formatDateTime(entry.transfer_datetime)}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function MatchingTab({ caseId, caseData }: { caseId: string; caseData: any }) {
  const [matches, setMatches] = useState<MatchResult[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSearching, setIsSearching] = useState(false);
  const [minScore, setMinScore] = useState(30);

  useEffect(() => {
    fetchMatches();
  }, [caseId]);

  const fetchMatches = async () => {
    setIsLoading(true);
    try {
      const data = await missingPersonsApi.getMatches(caseId);
      setMatches(data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFindMatches = async () => {
    setIsSearching(true);
    try {
      await missingPersonsApi.findMatches(caseId, minScore);
      await fetchMatches();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Search failed');
    } finally {
      setIsSearching(false);
    }
  };

  const handleConfirmMatch = async (matchId: string) => {
    const method = prompt('Enter confirmation method (DNA/visual/dental/fingerprint):');
    if (!method) return;
    try {
      await missingPersonsApi.confirmMatch(matchId, {
        confirmed_by_method: method,
        notes: 'Confirmed via FPMIS',
      });
      await fetchMatches();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Confirmation failed');
    }
  };

  const handleRejectMatch = async (matchId: string) => {
    const reason = prompt('Enter rejection reason:');
    try {
      await missingPersonsApi.rejectMatch(matchId, reason || undefined);
      await fetchMatches();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Rejection failed');
    }
  };

  if (isLoading) {
    return <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div></div>;
  }

  const deceased = caseData.deceased_info;
  const isIdentified = deceased?.is_identified;

  return (
    <div className="space-y-6">
      {}
      {isIdentified ? (
        <div className="card bg-green-50 border-green-200">
          <div className="card-body flex items-center gap-4">
            <CheckCircle className="w-8 h-8 text-green-600" />
            <div>
              <h3 className="font-semibold text-green-800">Body Identified</h3>
              <p className="text-green-700">This body has been positively identified as: {deceased?.name}</p>
            </div>
          </div>
        </div>
      ) : (
        <div className="card">
          <div className="card-header">
            <h2 className="font-semibold">Search for Matches</h2>
          </div>
          <div className="card-body">
            <p className="text-gray-600 mb-4">
              Search the missing persons database for potential matches based on physical characteristics.
            </p>
            <div className="flex items-end gap-4">
              <div>
                <label className="label">Minimum Match Score (%)</label>
                <input
                  type="number"
                  value={minScore}
                  onChange={(e) => setMinScore(parseInt(e.target.value))}
                  className="input w-32"
                  min="0"
                  max="100"
                />
              </div>
              <button
                onClick={handleFindMatches}
                disabled={isSearching}
                className="btn-primary flex items-center gap-2"
              >
                {isSearching ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    Searching...
                  </>
                ) : (
                  <>
                    <Search className="w-4 h-4" />
                    Find Matches
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {}
      <div className="card">
        <div className="card-header">
          <h2 className="font-semibold">Match Results ({matches.length})</h2>
        </div>
        <div className="card-body">
          {matches.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No matches found. Try running a search.</p>
          ) : (
            <div className="space-y-4">
              {matches.map((match: any) => (
                <div key={match.id} className={`p-4 border rounded-lg ${
                  match.status === 'confirmed' ? 'border-green-300 bg-green-50' :
                  match.status === 'rejected' ? 'border-red-300 bg-red-50' : ''
                }`}>
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-3">
                        <div className={`text-2xl font-bold ${
                          Number(match.match_score_percent) >= 80 ? 'text-green-600' :
                          Number(match.match_score_percent) >= 50 ? 'text-yellow-600' : 'text-red-600'
                        }`}>
                          {Number(match.match_score_percent).toFixed(0)}%
                        </div>
                        <div>
                          <p className="font-medium">{match.missing_person_name || 'Unknown'}</p>
                          <p className="text-sm text-gray-500">Report #{match.report_number}</p>
                        </div>
                      </div>
                      <div className="mt-2 text-sm text-gray-600">
                        <p>Last seen: {match.last_seen_location || 'Unknown'}</p>
                        {match.confidence_level && (
                          <p>Confidence: <span className="capitalize">{match.confidence_level}</span></p>
                        )}
                      </div>
                    </div>
                    <div className="flex flex-col items-end gap-2">
                      <span className={`badge ${
                        match.status === 'confirmed' ? 'bg-green-100 text-green-800' :
                        match.status === 'rejected' ? 'bg-red-100 text-red-800' :
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {match.status}
                      </span>
                      {match.status === 'potential' && (
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleConfirmMatch(match.id)}
                            className="btn-success text-xs py-1 px-2"
                          >
                            <CheckCircle className="w-3 h-3 mr-1" /> Confirm
                          </button>
                          <button
                            onClick={() => handleRejectMatch(match.id)}
                            className="btn-secondary text-xs py-1 px-2"
                          >
                            <XCircle className="w-3 h-3 mr-1" /> Reject
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between py-1">
      <span className="text-sm text-gray-500">{label}</span>
      <span className="text-sm text-gray-900 font-medium capitalize">{value}</span>
    </div>
  );
}

function StatBox({ icon: Icon, label, value, color }: { icon: any; label: string; value: string | number; color: string }) {
  const colors: Record<string, string> = {
    green: 'bg-green-100 text-green-600',
    yellow: 'bg-yellow-100 text-yellow-600',
    blue: 'bg-blue-100 text-blue-600',
    gray: 'bg-gray-100 text-gray-600',
  };

  return (
    <div className="text-center p-4 bg-gray-50 rounded-lg">
      <div className={`inline-flex p-2 rounded-lg mb-2 ${colors[color] || colors.gray}`}>
        <Icon className="w-5 h-5" />
      </div>
      <p className="text-lg font-bold text-gray-900">{value}</p>
      <p className="text-xs text-gray-500">{label}</p>
    </div>
  );
}
