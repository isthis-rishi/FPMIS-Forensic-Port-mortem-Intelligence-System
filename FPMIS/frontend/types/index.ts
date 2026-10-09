export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'admin' | 'forensic_doctor' | 'lab_technician' | 'mortuary_staff' | 'investigator' | 'viewer';
  institution_id?: string;
  phone?: string;
  designation?: string;
  is_active: boolean;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Institution {
  id: string;
  name: string;
  type: string;
  address?: string;
  district?: string;
  state?: string;
  is_active: boolean;
}

export interface Case {
  id: string;
  case_number: string;
  status: 'open' | 'in_progress' | 'pending_review' | 'completed' | 'closed';
  priority: 'low' | 'normal' | 'high' | 'urgent';
  case_type?: string;
  institution_id: string;
  police_station?: string;
  fir_number?: string;
  body_received_at?: string;
  created_by: string;
  assigned_doctor?: string;
  created_at: string;
}

export interface DeceasedInfo {
  id: string;
  case_id: string;
  is_identified: boolean;
  name?: string;
  age_years?: number;
  gender?: 'male' | 'female' | 'transgender' | 'unknown';
  height_cm?: number;
  weight_kg?: number;
  build?: string;
  complexion?: string;
  identification_marks?: string;
  district?: string;
}

export interface AutopsyReport {
  id: string;
  case_id: string;
  performed_by: string;
  cause_of_death_immediate?: string;
  cause_of_death_antecedent?: string;
  cause_of_death_underlying?: string;
  manner_of_death?: 'natural' | 'accident' | 'suicide' | 'homicide' | 'undetermined' | 'pending';
  external_examination?: string;
  internal_examination?: string;
  is_finalized: boolean;
  doctors_remarks?: string;
}

export interface Injury {
  id: string;
  case_id: string;
  injury_type: string;
  body_region: string;
  body_side?: string;
  length_cm?: number;
  width_cm?: number;
  depth_cm?: number;
  description?: string;
  probable_weapon?: string;
  is_fatal: boolean;
}

export interface Evidence {
  id: string;
  case_id: string;
  evidence_number: string;
  item_type: string;
  item_name: string;
  description?: string;
  status: string;
  collected_by: string;
  collected_at: string;
  current_holder?: string;
  current_location?: string;
}

export interface CustodyLog {
  id: string;
  evidence_id: string;
  action_type: string;
  from_user?: string;
  to_user?: string;
  from_location?: string;
  to_location?: string;
  transfer_datetime: string;
  purpose?: string;
}

export interface TODEstimation {
  id: string;
  case_id: string;
  body_temperature_celsius?: number;
  ambient_temperature_celsius?: number;
  rigor_mortis_overall?: number;
  livor_mortis_present?: boolean;
  livor_mortis_fixed?: boolean;
  estimated_tod_min_hours?: number;
  estimated_tod_max_hours?: number;
  estimated_datetime_min?: string;
  estimated_datetime_max?: string;
  confidence_level?: 'low' | 'medium' | 'high';
  calculation_reasoning?: string;
}

export interface DecompositionLog {
  id: string;
  case_id: string;
  stage: string;
  temperature_celsius?: number;
  humidity_percent?: number;
  location_type?: string;
  insect_activity_present?: boolean;
  logged_at: string;
}

export interface MissingPerson {
  id: string;
  report_number: string;
  name: string;
  age_years?: number;
  gender?: string;
  identification_marks?: string;
  last_seen_date: string;
  last_seen_location?: string;
  status: 'active' | 'found_alive' | 'found_deceased' | 'closed';
}

export interface MatchResult {
  id: string;
  case_id: string;
  missing_person_id: string;
  match_score_percent: number;
  confidence_level?: string;
  status: string;
  missing_person_name?: string;
  case_number?: string;
}

export interface Alert {
  id: string;
  alert_type: string;
  title: string;
  description?: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'new' | 'viewed' | 'investigating' | 'resolved' | 'dismissed';
  case_ids?: string[];
  region?: string;
  pattern_details?: string;
  generated_at: string;
}

export interface SearchResult {
  id: string;
  case_number: string;
  status: string;
  case_type?: string;
  created_at: string;
  deceased_name?: string;
  deceased_age?: number;
  deceased_gender?: string;
  is_identified: boolean;
  district?: string;
  cause_of_death?: string;
  manner_of_death?: string;
}

export interface SearchFilters {
  keyword?: string;
  status?: string;
  case_type?: string;
  gender?: string;
  age_min?: number;
  age_max?: number;
  district?: string;
  manner_of_death?: string;
  date_from?: string;
  date_to?: string;
}

export interface DashboardStats {
  total_cases: number;
  by_status: Record<string, number>;
  by_manner_of_death: Record<string, number>;
  by_gender: Record<string, number>;
  identified_vs_unidentified: { identified: number; unidentified: number };
  recent_30_days: number;
}

export interface AlertStats {
  total: number;
  new: number;
  investigating: number;
  resolved: number;
  by_severity: Record<string, number>;
}
