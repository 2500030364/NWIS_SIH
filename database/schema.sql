-- ============================================================================
-- NWIS (Nearby Wells Intelligence System) - Phase 1 Database Schema
-- Dialect: PostgreSQL 14+
-- Description: Core relational schema for well master data, stratigraphy,
--              high-frequency drilling telemetry, historical drilling incidents,
--              and daily/completion operational reports.
-- ============================================================================

-- Drop tables in reverse dependency order if re-initializing
DROP TABLE IF EXISTS reports CASCADE;
DROP TABLE IF EXISTS historical_events CASCADE;
DROP TABLE IF EXISTS drilling_parameters CASCADE;
DROP TABLE IF EXISTS formations CASCADE;
DROP TABLE IF EXISTS wells CASCADE;

-- ============================================================================
-- TABLE A: wells
-- Master catalog of drilling wells in the field / block.
-- ============================================================================
CREATE TABLE wells (
    id SERIAL PRIMARY KEY,
    well_name VARCHAR(50) UNIQUE NOT NULL,
    latitude NUMERIC(9, 6) NOT NULL,
    longitude NUMERIC(9, 6) NOT NULL,
    total_depth NUMERIC(8, 2) NOT NULL,
    status VARCHAR(20) NOT NULL,
    spud_date DATE NOT NULL,
    field_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT chk_wells_depth CHECK (total_depth > 0),
    CONSTRAINT chk_wells_lat CHECK (latitude BETWEEN -90.0 AND 90.0),
    CONSTRAINT chk_wells_lon CHECK (longitude BETWEEN -180.0 AND 180.0),
    CONSTRAINT chk_wells_status CHECK (status IN ('ACTIVE', 'COMPLETED', 'DRILLING', 'SUSPENDED', 'ABANDONED'))
);

COMMENT ON TABLE wells IS 'Master catalog of drilling wells with spatial coordinates and status';
COMMENT ON COLUMN wells.well_name IS 'Unique well identifier (e.g., NWIS-W001)';
COMMENT ON COLUMN wells.total_depth IS 'Target or final drilled true vertical depth in meters (m)';
COMMENT ON COLUMN wells.spud_date IS 'Date when drilling operations commenced at surface';

-- Indexes for spatial/field filtering and lookups
CREATE INDEX idx_wells_field_name ON wells(field_name);
CREATE INDEX idx_wells_status ON wells(status);
CREATE INDEX idx_wells_coordinates ON wells(latitude, longitude);


-- ============================================================================
-- TABLE B: formations
-- Stratigraphic geological intervals penetrated by each well.
-- ============================================================================
CREATE TABLE formations (
    id SERIAL PRIMARY KEY,
    well_id INT NOT NULL REFERENCES wells(id) ON DELETE CASCADE,
    formation_name VARCHAR(100) NOT NULL,
    top_depth NUMERIC(8, 2) NOT NULL,
    bottom_depth NUMERIC(8, 2) NOT NULL,

    -- Constraints
    CONSTRAINT chk_formations_depth_order CHECK (bottom_depth > top_depth),
    CONSTRAINT chk_formations_top_depth CHECK (top_depth >= 0)
);

COMMENT ON TABLE formations IS 'Stratigraphic layers / geological formations encountered per well';
COMMENT ON COLUMN formations.top_depth IS 'Top depth of formation boundary in meters';
COMMENT ON COLUMN formations.bottom_depth IS 'Bottom depth of formation boundary in meters';

-- Indexes for relational lookups and formation depth queries
CREATE INDEX idx_formations_well_id ON formations(well_id);
CREATE INDEX idx_formations_name ON formations(formation_name);
CREATE INDEX idx_formations_depth_range ON formations(well_id, top_depth, bottom_depth);


-- ============================================================================
-- TABLE C: drilling_parameters
-- High-frequency sensor telemetry captured during drilling operations.
-- ============================================================================
CREATE TABLE drilling_parameters (
    id BIGSERIAL PRIMARY KEY,
    well_id INT NOT NULL REFERENCES wells(id) ON DELETE CASCADE,
    recorded_at TIMESTAMPTZ NOT NULL,
    measured_depth NUMERIC(8, 2) NOT NULL,
    torque NUMERIC(8, 2) NOT NULL,
    wob NUMERIC(8, 2) NOT NULL,
    rop NUMERIC(8, 2) NOT NULL,
    rpm NUMERIC(8, 2) NOT NULL,
    mud_flow NUMERIC(8, 2) NOT NULL,
    mud_weight NUMERIC(6, 2) NOT NULL,
    standpipe_pressure NUMERIC(8, 2) NOT NULL,

    -- Constraints
    CONSTRAINT chk_drilling_params_depth CHECK (measured_depth >= 0),
    CONSTRAINT chk_drilling_params_torque CHECK (torque >= 0),
    CONSTRAINT chk_drilling_params_wob CHECK (wob >= 0),
    CONSTRAINT chk_drilling_params_rop CHECK (rop >= 0),
    CONSTRAINT chk_drilling_params_rpm CHECK (rpm >= 0),
    CONSTRAINT chk_drilling_params_flow CHECK (mud_flow >= 0),
    CONSTRAINT chk_drilling_params_mw CHECK (mud_weight > 0),
    CONSTRAINT chk_drilling_params_spp CHECK (standpipe_pressure >= 0)
);

COMMENT ON TABLE drilling_parameters IS 'Time-series and depth-indexed drilling sensor telemetry';
COMMENT ON COLUMN drilling_parameters.measured_depth IS 'Current drilled depth in meters (m)';
COMMENT ON COLUMN drilling_parameters.torque IS 'Surface rotary torque in kilo-Newton meters (kNm)';
COMMENT ON COLUMN drilling_parameters.wob IS 'Weight On Bit in kilo-pounds (klbf)';
COMMENT ON COLUMN drilling_parameters.rop IS 'Rate Of Penetration in meters per hour (m/hr)';
COMMENT ON COLUMN drilling_parameters.rpm IS 'Rotary table / top drive speed in revolutions per minute';
COMMENT ON COLUMN drilling_parameters.mud_flow IS 'Mud pump circulation rate in Liters per minute (L/min)';
COMMENT ON COLUMN drilling_parameters.mud_weight IS 'Drilling fluid specific gravity (SG, g/cm3)';
COMMENT ON COLUMN drilling_parameters.standpipe_pressure IS 'Standpipe pressure (SPP) in psi';

-- Indexes for time-series and depth-based telemetry lookup
CREATE INDEX idx_drilling_params_well_depth ON drilling_parameters(well_id, measured_depth);
CREATE INDEX idx_drilling_params_well_time ON drilling_parameters(well_id, recorded_at);


-- ============================================================================
-- TABLE D: historical_events
-- Recorded drilling incidents, hazards, anomalies, and NPT events.
-- ============================================================================
CREATE TABLE historical_events (
    id SERIAL PRIMARY KEY,
    well_id INT NOT NULL REFERENCES wells(id) ON DELETE CASCADE,
    depth NUMERIC(8, 2) NOT NULL,
    formation_id INT REFERENCES formations(id) ON DELETE SET NULL,
    event_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    description TEXT NOT NULL,
    cause TEXT,
    mitigation TEXT,
    event_time TIMESTAMPTZ NOT NULL,

    -- Constraints
    CONSTRAINT chk_historical_events_depth CHECK (depth >= 0),
    CONSTRAINT chk_historical_events_type CHECK (
        event_type IN (
            'MUD_LOSS',
            'STUCK_PIPE',
            'KICK',
            'TORQUE_SPIKE',
            'CEMENTING_ISSUE',
            'LOST_CIRCULATION',
            'HIGH_PRESSURE',
            'NPT'
        )
    ),
    CONSTRAINT chk_historical_events_severity CHECK (
        severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')
    )
);

COMMENT ON TABLE historical_events IS 'Drilling incidents, geological hazards, and non-productive time records';
COMMENT ON COLUMN historical_events.event_type IS 'Standardized drilling hazard classification';
COMMENT ON COLUMN historical_events.severity IS 'Operational severity level (LOW, MEDIUM, HIGH, CRITICAL)';
COMMENT ON COLUMN historical_events.cause IS 'Root cause analysis identified by drilling engineer / rig crew';
COMMENT ON COLUMN historical_events.mitigation IS 'Remedial actions taken to resolve incident';

-- Indexes for fast hazard queries across offset wells
CREATE INDEX idx_historical_events_well_id ON historical_events(well_id);
CREATE INDEX idx_historical_events_type ON historical_events(event_type);
CREATE INDEX idx_historical_events_severity ON historical_events(severity);
CREATE INDEX idx_historical_events_formation ON historical_events(formation_id);
CREATE INDEX idx_historical_events_depth ON historical_events(depth);


-- ============================================================================
-- TABLE E: reports
-- Document repository metadata and extracted text for drilling reports.
-- ============================================================================
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    well_id INT NOT NULL REFERENCES wells(id) ON DELETE CASCADE,
    report_name VARCHAR(150) NOT NULL,
    report_type VARCHAR(50) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    report_date DATE NOT NULL,
    extracted_text TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT chk_reports_type CHECK (
        report_type IN (
            'WCR',                -- Well Completion Report
            'DDR',                -- Daily Drilling Report
            'MUD_LOG',            -- Mud Logging Summary
            'COMPLETION_REPORT',  -- Final Completion Summary
            'DRILLING_REPORT'     -- Specialized Drilling/BHA Report
        )
    )
);

COMMENT ON TABLE reports IS 'Drilling operations reports and extracted textual content for NLP';
COMMENT ON COLUMN reports.report_type IS 'Standardized drilling document category';
COMMENT ON COLUMN reports.extracted_text IS 'Plain text content extracted from document for search';

-- Indexes for document search by well and type
CREATE INDEX idx_reports_well_id ON reports(well_id);
CREATE INDEX idx_reports_type ON reports(report_type);
CREATE INDEX idx_reports_date ON reports(report_date);
