-- ============================================
-- FPMIS - Forensic Post-Mortem Intelligence System
-- Complete Database Schema (PostgreSQL)
-- All 8 Modules
-- ============================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For fuzzy text search

-- ============================================
-- CORE TABLES (Authentication & Organization)
-- ============================================

-- Institutions (Hospitals, Labs, Medical Colleges)
CREATE TABLE institutions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('hospital', 'medical_college', 'laboratory', 'mortuary', 'police_station', 'other')),
    address TEXT,
    district VARCHAR(100),
    state VARCHAR(100),
    pincode VARCHAR(10),
    phone VARCHAR(20),
    email VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'forensic_doctor', 'lab_technician', 'mortuary_staff', 'investigator', 'viewer')),
    institution_id UUID REFERENCES institutions(id),
    phone VARCHAR(20),
    designation VARCHAR(100),
    license_number VARCHAR(100),  -- Medical license for doctors
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- MODULE 1: AUTOPSY REPORT STRUCTURING
-- ============================================

-- Main Case Table
CREATE TABLE cases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_number VARCHAR(50) UNIQUE NOT NULL,  -- Auto-generated: FPMIS/2026/001
    institution_id UUID NOT NULL REFERENCES institutions(id),
    
    -- Status tracking
    status VARCHAR(50) DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'pending_review', 'completed', 'closed')),
    priority VARCHAR(20) DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    
    -- Case metadata
    case_type VARCHAR(50) CHECK (case_type IN ('medico_legal', 'natural_death', 'accident', 'crime', 'mass_disaster', 'unknown')),
    police_station VARCHAR(255),
    fir_number VARCHAR(100),
    brought_by VARCHAR(255),  -- Who brought the body
    
    -- Timestamps
    body_received_at TIMESTAMP,
    autopsy_started_at TIMESTAMP,
    autopsy_completed_at TIMESTAMP,
    
    -- Users involved
    created_by UUID NOT NULL REFERENCES users(id),
    assigned_doctor UUID REFERENCES users(id),
    
    -- Soft delete
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Deceased Information
CREATE TABLE deceased_info (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_id UUID UNIQUE NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    
    -- Identity (may be unknown)
    is_identified BOOLEAN DEFAULT FALSE,
    name VARCHAR(255),
    alias VARCHAR(255),
    
    -- Demographics
    age_years INTEGER,
    age_months INTEGER,
    age_estimated BOOLEAN DEFAULT FALSE,  -- True if age is approximate
    gender VARCHAR(20) CHECK (gender IN ('male', 'female', 'transgender', 'unknown')),
    
    -- Physical description
    height_cm DECIMAL(5,2),
    weight_kg DECIMAL(5,2),
    build VARCHAR(50) CHECK (build IN ('thin', 'average', 'muscular', 'obese', 'unknown')),
    complexion VARCHAR(50),
    hair_color VARCHAR(50),
    hair_length VARCHAR(50),
    eye_color VARCHAR(50),
    
    -- Identification marks
    identification_marks TEXT,  -- Scars, tattoos, birthmarks
    dental_features TEXT,
    
    -- Address & Contact
    address TEXT,
    district VARCHAR(100),
    state VARCHAR(100),
    
    -- Next of kin
    relative_name VARCHAR(255),
    relative_relation VARCHAR(100),
    relative_phone VARCHAR(20),
    relative_address TEXT,
    
    -- Documents
    id_proof_type VARCHAR(50),
    id_proof_number VARCHAR(100),
    
    -- Photo references (stored as paths/URLs)
    photo_face VARCHAR(500),
    photo_full_body VARCHAR(500),
    photo_identification_marks VARCHAR(500),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Autopsy Report (Main findings)
CREATE TABLE autopsy_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_id UUID UNIQUE NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    
    -- Examining doctor
    performed_by UUID NOT NULL REFERENCES users(id),
    assisted_by TEXT,  -- Names of assistants
    
    -- External Examination
    general_appearance TEXT,
    clothing_description TEXT,
    post_mortem_changes TEXT,
    external_injuries TEXT,
    
    -- Detailed external findings (JSON for flexibility)
    head_face_findings TEXT,
    neck_findings TEXT,
    chest_findings TEXT,
    abdomen_findings TEXT,
    back_findings TEXT,
    upper_limbs_findings TEXT,
    lower_limbs_findings TEXT,
    genitalia_findings TEXT,
    
    -- Internal Examination
    -- Head
    scalp_skull TEXT,
    brain_findings TEXT,
    brain_weight_gm DECIMAL(6,2),
    
    -- Neck
    neck_structures TEXT,
    hyoid_bone TEXT,
    thyroid_cartilage TEXT,
    
    -- Thorax
    chest_cavity TEXT,
    lungs_findings TEXT,
    lungs_weight_left_gm DECIMAL(6,2),
    lungs_weight_right_gm DECIMAL(6,2),
    heart_findings TEXT,
    heart_weight_gm DECIMAL(6,2),
    major_vessels TEXT,
    
    -- Abdomen
    abdominal_cavity TEXT,
    liver_findings TEXT,
    liver_weight_gm DECIMAL(6,2),
    spleen_findings TEXT,
    spleen_weight_gm DECIMAL(6,2),
    kidneys_findings TEXT,
    kidneys_weight_left_gm DECIMAL(6,2),
    kidneys_weight_right_gm DECIMAL(6,2),
    stomach_contents TEXT,
    intestines_findings TEXT,
    
    -- Pelvis
    bladder_findings TEXT,
    uterus_findings TEXT,  -- If applicable
    prostate_findings TEXT,  -- If applicable
    
    -- Spine
    spine_findings TEXT,
    spinal_cord TEXT,
    
    -- Cause of Death
    cause_of_death_immediate VARCHAR(500),  -- 1(a) - Final disease/condition
    cause_of_death_antecedent VARCHAR(500),  -- 1(b) - Due to
    cause_of_death_underlying VARCHAR(500),  -- 1(c) - Due to
    cause_of_death_contributing TEXT,  -- Part 2 - Contributing factors
    
    manner_of_death VARCHAR(50) CHECK (manner_of_death IN ('natural', 'accident', 'suicide', 'homicide', 'undetermined', 'pending')),
    
    -- Additional
    special_dissections TEXT,  -- Any special procedures
    samples_collected TEXT,  -- Samples sent for analysis
    doctors_remarks TEXT,
    
    -- Signatures
    is_finalized BOOLEAN DEFAULT FALSE,
    finalized_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Injuries Catalog (Detailed injury documentation)
CREATE TABLE injuries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    
    injury_type VARCHAR(50) NOT NULL CHECK (injury_type IN (
        'abrasion', 'bruise', 'laceration', 'incised_wound', 'stab_wound',
        'gunshot_wound', 'burn', 'fracture', 'dislocation', 'bite_mark',
        'ligature_mark', 'defense_wound', 'other'
    )),
    
    body_region VARCHAR(100) NOT NULL,
    body_side VARCHAR(20) CHECK (body_side IN ('left', 'right', 'midline', 'bilateral')),
    
    -- Measurements
    length_cm DECIMAL(5,2),
    width_cm DECIMAL(5,2),
    depth_cm DECIMAL(5,2),
    
    -- Description
    description TEXT,
    probable_weapon VARCHAR(255),
    age_of_injury VARCHAR(100),  -- Fresh, healing, old
    
    -- Significance
    is_fatal BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- MODULE 2: TIME-OF-DEATH ESTIMATION
-- ============================================

CREATE TABLE time_of_death_estimations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_id UUID UNIQUE NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    
    -- Input parameters
    body_temperature_celsius DECIMAL(4,2),
    ambient_temperature_celsius DECIMAL(4,2),
    body_weight_kg DECIMAL(5,2),
    clothing_description VARCHAR(255),
    body_position VARCHAR(100),
    environment VARCHAR(50) CHECK (environment IN ('indoor', 'outdoor', 'water', 'buried', 'enclosed_space')),
    
    -- Rigor mortis (0-4 scale)
    rigor_mortis_jaw INTEGER CHECK (rigor_mortis_jaw BETWEEN 0 AND 4),
    rigor_mortis_neck INTEGER CHECK (rigor_mortis_neck BETWEEN 0 AND 4),
    rigor_mortis_upper_limbs INTEGER CHECK (rigor_mortis_upper_limbs BETWEEN 0 AND 4),
    rigor_mortis_lower_limbs INTEGER CHECK (rigor_mortis_lower_limbs BETWEEN 0 AND 4),
    rigor_mortis_overall INTEGER CHECK (rigor_mortis_overall BETWEEN 0 AND 4),
    
    -- Livor mortis
    livor_mortis_present BOOLEAN,
    livor_mortis_color VARCHAR(50),
    livor_mortis_distribution TEXT,
    livor_mortis_fixed BOOLEAN,
    
    -- Other signs
    corneal_opacity INTEGER CHECK (corneal_opacity BETWEEN 0 AND 4),
    tache_noire BOOLEAN,
    decomposition_started BOOLEAN,
    insect_activity TEXT,
    
    -- Calculated results
    estimated_tod_min_hours DECIMAL(5,2),
    estimated_tod_max_hours DECIMAL(5,2),
    estimated_tod_datetime_min TIMESTAMP,
    estimated_tod_datetime_max TIMESTAMP,
    confidence_level VARCHAR(20) CHECK (confidence_level IN ('low', 'medium', 'high')),
    
    -- Calculation details
    calculation_method VARCHAR(100),
    calculation_reasoning TEXT,
    calculation_parameters_json JSONB,  -- Store all input params for audit
    
    -- Manual override
    is_manually_adjusted BOOLEAN DEFAULT FALSE,
    manual_tod_min TIMESTAMP,
    manual_tod_max TIMESTAMP,
    manual_adjustment_reason TEXT,
    
    calculated_by UUID REFERENCES users(id),
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- MODULE 3: DECOMPOSITION & ENVIRONMENTAL LOGGING
-- ============================================

CREATE TABLE decomposition_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    
    -- Decomposition stage
    stage VARCHAR(50) NOT NULL CHECK (stage IN (
        'fresh', 
        'early_decomposition',  -- Bloating starting
        'bloat',  -- Full bloating
        'active_decay', 
        'advanced_decay', 
        'dry_remains',
        'skeletonization'
    )),
    stage_numeric INTEGER CHECK (stage_numeric BETWEEN 1 AND 7),  -- For calculations
    
    -- Environmental conditions
    temperature_celsius DECIMAL(5,2),
    humidity_percent DECIMAL(5,2),
    weather_condition VARCHAR(100),
    location_type VARCHAR(50) CHECK (location_type IN ('indoor', 'outdoor', 'water', 'buried', 'vehicle', 'other')),
    sun_exposure VARCHAR(50) CHECK (sun_exposure IN ('none', 'partial', 'full')),
    
    -- Observations
    skin_changes TEXT,
    discoloration TEXT,
    bloating_level VARCHAR(20),
    purging_present BOOLEAN,
    marbling_present BOOLEAN,
    skin_slippage BOOLEAN,
    
    -- Insect activity
    insect_activity_present BOOLEAN,
    insect_types TEXT,
    maggot_mass_present BOOLEAN,
    maggot_stage VARCHAR(50),
    
    -- Other observations
    odor_level VARCHAR(20) CHECK (odor_level IN ('none', 'slight', 'moderate', 'strong', 'overwhelming')),
    animal_activity TEXT,
    additional_observations TEXT,
    
    -- Photos
    photo_references TEXT,
    
    -- Logging info
    logged_by UUID NOT NULL REFERENCES users(id),
    logged_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- MODULE 4: EVIDENCE CHAIN-OF-CUSTODY
-- ============================================

-- Evidence Items
CREATE TABLE evidence_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    
    -- Evidence identification
    evidence_number VARCHAR(50) NOT NULL,  -- Local evidence number
    barcode VARCHAR(100),
    
    -- Evidence details
    item_type VARCHAR(50) NOT NULL CHECK (item_type IN (
        'biological_sample', 'clothing', 'weapon', 'document', 
        'electronic', 'toxicology_sample', 'dna_sample', 
        'photograph', 'personal_belongings', 'other'
    )),
    item_name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Collection details
    collected_from VARCHAR(255),  -- Location on body or scene
    collection_method VARCHAR(255),
    quantity VARCHAR(100),
    condition_when_collected VARCHAR(255),
    
    -- Storage
    storage_location VARCHAR(255),
    storage_requirements TEXT,
    
    -- Status
    status VARCHAR(50) DEFAULT 'in_custody' CHECK (status IN (
        'in_custody', 'sent_for_analysis', 'in_analysis', 
        'analysis_complete', 'returned', 'disposed', 'lost'
    )),
    
    -- Analysis
    sent_to_lab VARCHAR(255),
    analysis_type VARCHAR(255),
    analysis_result TEXT,
    analysis_report_reference VARCHAR(255),
    
    -- Collection info
    collected_by UUID NOT NULL REFERENCES users(id),
    collected_at TIMESTAMP NOT NULL,
    
    -- Current holder
    current_holder UUID REFERENCES users(id),
    current_location VARCHAR(255),
    
    -- Disposal
    disposal_date DATE,
    disposal_method VARCHAR(255),
    disposal_authorized_by UUID REFERENCES users(id),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(case_id, evidence_number)
);

-- Chain of Custody Log (Every transfer recorded)
CREATE TABLE chain_of_custody (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    evidence_id UUID NOT NULL REFERENCES evidence_items(id) ON DELETE CASCADE,
    
    -- Transfer details
    action_type VARCHAR(50) NOT NULL CHECK (action_type IN (
        'collected', 'transferred', 'received', 'stored', 
        'retrieved', 'sent_for_analysis', 'returned_from_analysis',
        'photographed', 'examined', 'disposed'
    )),
    
    -- Who
    from_user UUID REFERENCES users(id),  -- NULL if initial collection
    to_user UUID REFERENCES users(id),    -- NULL if disposal
    performed_by UUID NOT NULL REFERENCES users(id),
    
    -- Where & When
    from_location VARCHAR(255),
    to_location VARCHAR(255),
    transfer_datetime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Condition
    condition_at_transfer VARCHAR(255),
    
    -- Purpose & Notes
    purpose TEXT,
    notes TEXT,
    
    -- Verification
    received_signature_reference VARCHAR(255),  -- Could store digital signature ID
    witness_name VARCHAR(255),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- MODULE 5: MISSING PERSON & BODY MATCHING
-- ============================================

-- Missing Persons Reports
CREATE TABLE missing_persons (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Report info
    report_number VARCHAR(50) UNIQUE NOT NULL,
    reported_by VARCHAR(255) NOT NULL,
    reporter_relation VARCHAR(100),
    reporter_phone VARCHAR(20),
    reporter_address TEXT,
    
    -- Missing person details
    name VARCHAR(255) NOT NULL,
    alias VARCHAR(255),
    
    -- Demographics
    age_years INTEGER,
    age_approximate BOOLEAN DEFAULT FALSE,
    gender VARCHAR(20) CHECK (gender IN ('male', 'female', 'transgender', 'unknown')),
    
    -- Physical description
    height_cm_min DECIMAL(5,2),
    height_cm_max DECIMAL(5,2),
    weight_kg_min DECIMAL(5,2),
    weight_kg_max DECIMAL(5,2),
    build VARCHAR(50),
    complexion VARCHAR(50),
    hair_color VARCHAR(50),
    hair_style VARCHAR(100),
    eye_color VARCHAR(50),
    
    -- Identification marks
    identification_marks TEXT,
    scars TEXT,
    tattoos TEXT,
    birthmarks TEXT,
    dental_features TEXT,
    deformities TEXT,
    
    -- Last seen
    last_seen_date DATE NOT NULL,
    last_seen_time TIME,
    last_seen_location TEXT,
    last_seen_district VARCHAR(100),
    last_seen_state VARCHAR(100),
    last_seen_wearing TEXT,
    
    -- Additional info
    medical_conditions TEXT,
    medications TEXT,
    mental_health_notes TEXT,
    
    -- Photos
    photo_recent VARCHAR(500),
    photo_additional TEXT,  -- JSON array of URLs
    
    -- Status
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'found_alive', 'found_deceased', 'closed')),
    matched_case_id UUID REFERENCES cases(id),
    
    -- Police info
    police_station VARCHAR(255),
    fir_number VARCHAR(100),
    investigating_officer VARCHAR(255),
    officer_phone VARCHAR(20),
    
    -- Metadata
    entered_by UUID REFERENCES users(id),
    source VARCHAR(100),  -- Where did this report come from
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Potential Matches (Unidentified Body ↔ Missing Person)
CREATE TABLE body_match_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    case_id UUID NOT NULL REFERENCES cases(id),  -- Unidentified body
    missing_person_id UUID NOT NULL REFERENCES missing_persons(id),
    
    -- Match score
    match_score_percent DECIMAL(5,2) NOT NULL,
    confidence_level VARCHAR(20) CHECK (confidence_level IN ('low', 'medium', 'high', 'confirmed')),
    
    -- Score breakdown (JSON)
    score_breakdown JSONB,
    /*
    {
        "gender": {"score": 20, "max": 20, "match": true},
        "age": {"score": 15, "max": 15, "difference": 2},
        "height": {"score": 10, "max": 15, "difference_cm": 3},
        "identification_marks": {"score": 18, "max": 20, "matches": ["scar on left arm"]},
        ...
    }
    */
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN (
        'pending', 'under_review', 'probable_match', 
        'confirmed', 'rejected', 'dna_pending'
    )),
    
    -- Review
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMP,
    review_notes TEXT,
    
    -- Confirmation
    confirmed_by UUID REFERENCES users(id),
    confirmed_at TIMESTAMP,
    confirmation_method VARCHAR(100),  -- DNA, visual, dental, fingerprint, etc.
    
    -- Algorithm info
    algorithm_version VARCHAR(50),
    matched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(case_id, missing_person_id)
);

-- ============================================
-- MODULE 6: INTELLIGENCE DATABASE (Search & Filters)
-- (Handled by indexes and queries on existing tables)
-- ============================================

-- Full-text search indexes
CREATE INDEX idx_cases_fts ON cases USING gin(to_tsvector('english', case_number || ' ' || COALESCE(police_station, '') || ' ' || COALESCE(fir_number, '')));
CREATE INDEX idx_deceased_fts ON deceased_info USING gin(to_tsvector('english', COALESCE(name, '') || ' ' || COALESCE(identification_marks, '') || ' ' || COALESCE(address, '')));
CREATE INDEX idx_autopsy_fts ON autopsy_reports USING gin(to_tsvector('english', COALESCE(cause_of_death_immediate, '') || ' ' || COALESCE(doctors_remarks, '')));

-- Trigram indexes for fuzzy matching
CREATE INDEX idx_deceased_name_trgm ON deceased_info USING gin(name gin_trgm_ops);
CREATE INDEX idx_missing_name_trgm ON missing_persons USING gin(name gin_trgm_ops);

-- Filter indexes
CREATE INDEX idx_cases_status ON cases(status);
CREATE INDEX idx_cases_institution ON cases(institution_id);
CREATE INDEX idx_cases_created ON cases(created_at);
CREATE INDEX idx_autopsy_manner ON autopsy_reports(manner_of_death);
CREATE INDEX idx_autopsy_cause ON autopsy_reports(cause_of_death_immediate);
CREATE INDEX idx_deceased_gender ON deceased_info(gender);
CREATE INDEX idx_deceased_age ON deceased_info(age_years);
CREATE INDEX idx_deceased_district ON deceased_info(district);

-- ============================================
-- MODULE 7: CASE HISTORY & COMPARISON
-- (Handled by queries, but we add a saved comparisons table)
-- ============================================

CREATE TABLE saved_comparisons (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    name VARCHAR(255),
    description TEXT,
    
    -- Cases being compared (array of UUIDs)
    case_ids UUID[] NOT NULL,
    
    -- Comparison settings
    comparison_fields TEXT[],  -- Which fields to compare
    
    -- Results snapshot (optional, for quick loading)
    comparison_result_json JSONB,
    
    -- User who saved it
    created_by UUID NOT NULL REFERENCES users(id),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- MODULE 8: PATTERN-BASED ALERTS
-- ============================================

-- Alert Definitions (What patterns to look for)
CREATE TABLE alert_rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    rule_type VARCHAR(50) NOT NULL CHECK (rule_type IN (
        'cluster',           -- Multiple similar deaths in region/time
        'unusual_cause',     -- Rare cause of death
        'unidentified',      -- Body unidentified too long
        'trend',             -- Sudden increase in death type
        'toxin',             -- Specific toxin detected
        'custom'             -- Custom SQL condition
    )),
    
    -- Rule parameters (JSON)
    parameters JSONB NOT NULL,
    /*
    Cluster example:
    {
        "min_cases": 3,
        "time_window_days": 30,
        "region_level": "district",
        "cause_similarity": true
    }
    
    Unusual cause example:
    {
        "causes": ["cyanide", "arsenic", "thallium"],
        "notify_immediately": true
    }
    */
    
    -- Severity
    severity VARCHAR(20) DEFAULT 'medium' CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Notification settings
    notify_roles TEXT[],  -- Which roles to notify
    notify_emails TEXT[],  -- Additional emails
    
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Generated Alerts
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Link to rule that generated it
    rule_id UUID REFERENCES alert_rules(id),
    
    -- Alert details
    alert_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    
    -- Related data
    case_ids UUID[],  -- Cases involved in this alert
    region VARCHAR(255),
    
    -- Detection info
    detection_parameters JSONB,
    pattern_details TEXT,
    
    -- Status
    status VARCHAR(50) DEFAULT 'new' CHECK (status IN ('new', 'viewed', 'investigating', 'resolved', 'dismissed')),
    
    -- Response
    assigned_to UUID REFERENCES users(id),
    viewed_by UUID REFERENCES users(id),
    viewed_at TIMESTAMP,
    resolved_by UUID REFERENCES users(id),
    resolved_at TIMESTAMP,
    resolution_notes TEXT,
    
    -- Auto-generated
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Alert Notifications (Track who was notified)
CREATE TABLE alert_notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    alert_id UUID NOT NULL REFERENCES alerts(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),
    
    notification_method VARCHAR(50) CHECK (notification_method IN ('in_app', 'email', 'sms')),
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- AUDIT LOG (For compliance & tracking)
-- ============================================

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Who
    user_id UUID REFERENCES users(id),
    user_email VARCHAR(255),
    user_role VARCHAR(50),
    
    -- What
    action VARCHAR(50) NOT NULL,  -- CREATE, UPDATE, DELETE, VIEW, EXPORT, LOGIN, etc.
    entity_type VARCHAR(50) NOT NULL,  -- cases, autopsy_reports, evidence_items, etc.
    entity_id UUID,
    
    -- Details
    old_values JSONB,
    new_values JSONB,
    description TEXT,
    
    -- Where
    ip_address VARCHAR(45),
    user_agent TEXT,
    
    -- When
    performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_time ON audit_logs(performed_at);

-- ============================================
-- HELPER VIEWS
-- ============================================

-- Case Summary View (for dashboard and listings)
CREATE VIEW case_summary AS
SELECT 
    c.id,
    c.case_number,
    c.status,
    c.priority,
    c.case_type,
    c.created_at,
    c.body_received_at,
    i.name as institution_name,
    d.name as deceased_name,
    d.age_years,
    d.gender,
    d.is_identified,
    ar.manner_of_death,
    ar.cause_of_death_immediate,
    ar.is_finalized,
    u.full_name as created_by_name,
    doc.full_name as assigned_doctor_name,
    (SELECT COUNT(*) FROM evidence_items e WHERE e.case_id = c.id) as evidence_count,
    (SELECT COUNT(*) FROM injuries inj WHERE inj.case_id = c.id) as injury_count
FROM cases c
LEFT JOIN institutions i ON c.institution_id = i.id
LEFT JOIN deceased_info d ON d.case_id = c.id
LEFT JOIN autopsy_reports ar ON ar.case_id = c.id
LEFT JOIN users u ON c.created_by = u.id
LEFT JOIN users doc ON c.assigned_doctor = doc.id
WHERE c.is_deleted = FALSE;

-- Unidentified Bodies View (for matching)
CREATE VIEW unidentified_bodies AS
SELECT 
    c.id as case_id,
    c.case_number,
    d.*,
    c.body_received_at,
    c.created_at,
    i.name as institution_name,
    i.district as institution_district
FROM cases c
JOIN deceased_info d ON d.case_id = c.id
JOIN institutions i ON c.institution_id = i.id
WHERE d.is_identified = FALSE
AND c.is_deleted = FALSE
AND c.status != 'closed';

-- ============================================
-- INITIAL DATA (Default alert rules)
-- ============================================

INSERT INTO alert_rules (name, description, rule_type, parameters, severity) VALUES
(
    'Death Cluster Detection',
    'Alerts when 3+ deaths with similar cause occur in same district within 30 days',
    'cluster',
    '{"min_cases": 3, "time_window_days": 30, "region_level": "district", "cause_similarity": true}',
    'high'
),
(
    'Poison/Toxin Alert',
    'Immediate alert for suspected poisoning cases',
    'unusual_cause',
    '{"keywords": ["poison", "cyanide", "arsenic", "organophosphate", "thallium", "mercury"], "notify_immediately": true}',
    'critical'
),
(
    'Unidentified Body Alert',
    'Alert for bodies unidentified after 7 days',
    'unidentified',
    '{"days_threshold": 7}',
    'medium'
),
(
    'Mass Casualty Trend',
    'Alert when daily deaths exceed 2x normal average',
    'trend',
    '{"threshold_multiplier": 2, "baseline_days": 30}',
    'high'
);

-- ============================================
-- FUNCTIONS & TRIGGERS
-- ============================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply to all tables with updated_at
CREATE TRIGGER update_institutions_updated_at BEFORE UPDATE ON institutions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_cases_updated_at BEFORE UPDATE ON cases FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_deceased_updated_at BEFORE UPDATE ON deceased_info FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_autopsy_updated_at BEFORE UPDATE ON autopsy_reports FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_tod_updated_at BEFORE UPDATE ON time_of_death_estimations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_evidence_updated_at BEFORE UPDATE ON evidence_items FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_missing_updated_at BEFORE UPDATE ON missing_persons FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_match_updated_at BEFORE UPDATE ON body_match_results FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_comparisons_updated_at BEFORE UPDATE ON saved_comparisons FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_alert_rules_updated_at BEFORE UPDATE ON alert_rules FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_alerts_updated_at BEFORE UPDATE ON alerts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Auto-generate case number
CREATE OR REPLACE FUNCTION generate_case_number()
RETURNS TRIGGER AS $$
DECLARE
    year_part VARCHAR(4);
    sequence_num INTEGER;
BEGIN
    year_part := EXTRACT(YEAR FROM CURRENT_DATE)::VARCHAR;
    
    SELECT COALESCE(MAX(
        CAST(SPLIT_PART(case_number, '/', 3) AS INTEGER)
    ), 0) + 1 INTO sequence_num
    FROM cases
    WHERE case_number LIKE 'FPMIS/' || year_part || '/%';
    
    NEW.case_number := 'FPMIS/' || year_part || '/' || LPAD(sequence_num::VARCHAR, 5, '0');
    
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER auto_case_number
    BEFORE INSERT ON cases
    FOR EACH ROW
    WHEN (NEW.case_number IS NULL OR NEW.case_number = '')
    EXECUTE FUNCTION generate_case_number();

-- ============================================
-- END OF SCHEMA
-- ============================================
