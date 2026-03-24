-- Senate Database Schema

-- Create Province table
CREATE TABLE IF NOT EXISTS Province (
    UniqueID SERIAL PRIMARY KEY,
    Name VARCHAR(255) NOT NULL UNIQUE
);

-- Create Party table
CREATE TABLE IF NOT EXISTS Party (
    UniqueID SERIAL PRIMARY KEY,
    Name VARCHAR(255) NOT NULL UNIQUE
);

-- Create Attendance table (lookup table)
CREATE TABLE IF NOT EXISTS Attendance (
    UniqueID SERIAL PRIMARY KEY,
    Name VARCHAR(100) NOT NULL
);

-- Create Vote table (lookup table)
CREATE TABLE IF NOT EXISTS Vote (
    UniqueID SERIAL PRIMARY KEY,
    Name VARCHAR(100) NOT NULL
);

-- Create SessionType table (lookup table)
CREATE TABLE IF NOT EXISTS SessionType (
    UniqueID SERIAL PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Short_name VARCHAR(10) NOT NULL
);

-- Create SenateSession table
CREATE TABLE IF NOT EXISTS SenateSession (
    UniqueID SERIAL PRIMARY KEY,
    Date DATE NOT NULL,
    Session_type_id INTEGER,
    FOREIGN KEY (Session_type_id) REFERENCES SessionType(UniqueID) ON DELETE RESTRICT
);

-- Create SessionFile table
CREATE TABLE IF NOT EXISTS SessionFile (
    UniqueID SERIAL PRIMARY KEY,
    SenateSession_id INTEGER NOT NULL,
    File_hash VARCHAR(64) NOT NULL UNIQUE,
    File_name VARCHAR(255) NOT NULL,
    File_size INTEGER NOT NULL,
    Upload_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (SenateSession_id) REFERENCES SenateSession(UniqueID) ON DELETE CASCADE
);

-- Create Coalition table (Bloque)
CREATE TABLE IF NOT EXISTS Coalition (
    UniqueID SERIAL PRIMARY KEY,
    Name VARCHAR(255) NOT NULL UNIQUE
);

-- Create Representative table
CREATE TABLE IF NOT EXISTS Representative (
    UniqueID UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    External_id VARCHAR(50),
    Full_name VARCHAR(255) NOT NULL,
    Last_name VARCHAR(255),
    First_name VARCHAR(255),
    Province_id INTEGER NOT NULL,
    Party_id INTEGER NOT NULL,
    Coalition_id INTEGER,
    Legal_start_date DATE,
    Legal_end_date DATE,
    Real_start_date DATE,
    Real_end_date VARCHAR(50),
    Email VARCHAR(255),
    Phone VARCHAR(100),
    Photo_url TEXT,
    Facebook_url TEXT,
    Twitter_url TEXT,
    Instagram_url TEXT,
    Youtube_url TEXT,
    FOREIGN KEY (Province_id) REFERENCES Province(UniqueID) ON DELETE RESTRICT,
    FOREIGN KEY (Party_id) REFERENCES Party(UniqueID) ON DELETE RESTRICT,
    FOREIGN KEY (Coalition_id) REFERENCES Coalition(UniqueID) ON DELETE SET NULL
);

-- Create Topic table
CREATE TABLE IF NOT EXISTS Topic (
    UniqueID SERIAL PRIMARY KEY,
    SenateSession_id INTEGER NOT NULL,
    Name TEXT NOT NULL,
    FOREIGN KEY (SenateSession_id) REFERENCES SenateSession(UniqueID) ON DELETE CASCADE
);

-- Create RepresentativeTopicSummary table
CREATE TABLE IF NOT EXISTS RepresentativeTopicSummary (
    UniqueID SERIAL PRIMARY KEY,
    Representative_id UUID NOT NULL,
    Topic_id INTEGER NOT NULL,
    Summary TEXT NOT NULL,
    FOREIGN KEY (Representative_id) REFERENCES Representative(UniqueID) ON DELETE CASCADE,
    FOREIGN KEY (Topic_id) REFERENCES Topic(UniqueID) ON DELETE CASCADE,
    UNIQUE (Representative_id, Topic_id)
);

-- Create AttendanceSession table
CREATE TABLE IF NOT EXISTS AttendanceSession (
    UniqueID SERIAL PRIMARY KEY,
    Representative_id UUID NOT NULL,
    SenateSession_id INTEGER NOT NULL,
    Attendance_id INTEGER NOT NULL,
    FOREIGN KEY (Representative_id) REFERENCES Representative(UniqueID) ON DELETE CASCADE,
    FOREIGN KEY (SenateSession_id) REFERENCES SenateSession(UniqueID) ON DELETE CASCADE,
    FOREIGN KEY (Attendance_id) REFERENCES Attendance(UniqueID) ON DELETE RESTRICT
);

-- Create VoteSession table
CREATE TABLE IF NOT EXISTS VoteSession (
    UniqueID SERIAL PRIMARY KEY,
    Representative_id UUID NOT NULL,
    SenateSession_id INTEGER NOT NULL,
    Topic_id INTEGER NOT NULL,
    Vote_id INTEGER NOT NULL,
    FOREIGN KEY (Representative_id) REFERENCES Representative(UniqueID) ON DELETE CASCADE,
    FOREIGN KEY (SenateSession_id) REFERENCES SenateSession(UniqueID) ON DELETE CASCADE,
    FOREIGN KEY (Topic_id) REFERENCES Topic(UniqueID) ON DELETE CASCADE,
    FOREIGN KEY (Vote_id) REFERENCES Vote(UniqueID) ON DELETE RESTRICT
);

-- Create Intervention table
CREATE TABLE IF NOT EXISTS Intervention (
    UniqueID SERIAL PRIMARY KEY,
    Topic_id INTEGER NOT NULL,
    Representative_id UUID NOT NULL,
    Text TEXT NOT NULL,
    Role VARCHAR(100),
    Intervention_order INTEGER,
    FOREIGN KEY (Topic_id) REFERENCES Topic(UniqueID) ON DELETE CASCADE,
    FOREIGN KEY (Representative_id) REFERENCES Representative(UniqueID) ON DELETE CASCADE
);

-- Create indexes for better query performance
CREATE INDEX idx_representative_province ON Representative(Province_id);
CREATE INDEX idx_representative_party ON Representative(Party_id);
CREATE INDEX idx_representative_coalition ON Representative(Coalition_id);
CREATE INDEX idx_representative_external_id ON Representative(External_id);
CREATE INDEX idx_session_file_hash ON SessionFile(File_hash);
CREATE INDEX idx_session_file_senate_session ON SessionFile(SenateSession_id);
CREATE INDEX idx_senate_session_type ON SenateSession(Session_type_id);
CREATE INDEX idx_topic_session ON Topic(SenateSession_id);
CREATE INDEX idx_rep_topic_summary_representative ON RepresentativeTopicSummary(Representative_id);
CREATE INDEX idx_rep_topic_summary_topic ON RepresentativeTopicSummary(Topic_id);
CREATE INDEX idx_attendance_session_representative ON AttendanceSession(Representative_id);
CREATE INDEX idx_attendance_session_senate ON AttendanceSession(SenateSession_id);
CREATE INDEX idx_vote_session_representative ON VoteSession(Representative_id);
CREATE INDEX idx_vote_session_senate ON VoteSession(SenateSession_id);
CREATE INDEX idx_vote_session_topic ON VoteSession(Topic_id);
CREATE INDEX idx_intervention_topic ON Intervention(Topic_id);
CREATE INDEX idx_intervention_representative ON Intervention(Representative_id);
CREATE INDEX idx_intervention_order ON Intervention(Topic_id, Intervention_order);

-- Insert sample data for lookup tables
INSERT INTO Attendance (Name) VALUES 
    ('Presente'),
    ('Ausente')
ON CONFLICT DO NOTHING;

INSERT INTO Vote (Name) VALUES 
    ('Afirmativo'),
    ('Negativo'),
    ('Abstención'),
    ('Ausente')
ON CONFLICT DO NOTHING;

INSERT INTO SessionType (Name, Short_name) VALUES 
    ('ASAMBLEA', 'AS'),
    ('EN MINORIA', 'MI'),
    ('ESPECIAL', 'ES'),
    ('ESPECIAL EXTRAORDINARIA', 'EE'),
    ('EXTRAORDINARIA', 'EX'),
    ('INFORMATIVA ESPECIAL', 'IE'),
    ('ORDINARIA', 'OR'),
    ('ORDINARIA CONTINUACION', 'OC'),
    ('PREPARATORIA', 'PA'),
    ('TRIBUNAL DE JUICIO POLITICO', 'TR')
ON CONFLICT DO NOTHING;

-- Insert Provinces
INSERT INTO Province (Name) VALUES 
    ('BUENOS AIRES'),
    ('CATAMARCA'),
    ('CHACO'),
    ('CHUBUT'),
    ('CIUDAD AUTÓNOMA DE BUENOS AIRES'),
    ('CORRIENTES'),
    ('CÓRDOBA'),
    ('ENTRE RÍOS'),
    ('FORMOSA'),
    ('JUJUY'),
    ('LA PAMPA'),
    ('LA RIOJA'),
    ('MENDOZA'),
    ('MISIONES'),
    ('NEUQUÉN'),
    ('RÍO NEGRO'),
    ('SALTA'),
    ('SAN JUAN'),
    ('SAN LUIS'),
    ('SANTA CRUZ'),
    ('SANTA FE'),
    ('SANTIAGO DEL ESTERO'),
    ('TIERRA DEL FUEGO, ANTÁRTIDA E ISLAS DEL ATLÁNTICO SUR'),
    ('TUCUMÁN')
ON CONFLICT DO NOTHING;

-- Insert Parties
INSERT INTO Party (Name) VALUES 
    ('ALIANZA FRENTE DE TODOS'),
    ('ALIANZA LA LIBERTAD AVANZA'),
    ('ALIANZA POR SANTA CRUZ'),
    ('ALIANZA UNIÓN POR LA PATRIA'),
    ('ECO + VAMOS CORRIENTES'),
    ('FRENTE CAMBIA MENDOZA'),
    ('FRENTE CÍVICO POR SANTIAGO'),
    ('FRENTE DE TODOS'),
    ('FRENTE FUERZA PATRIA PERONISTA'),
    ('FRENTE RENOVADOR DE LA CONCORDIA-INNOVACIÓN FEDERAL'),
    ('FRENTE TODOS'),
    ('FUERZA ENTRE RÍOS'),
    ('FUERZA PATRIA'),
    ('HACEMOS POR CÓRDOBA'),
    ('JUNTOS POR EL CAMBIO'),
    ('JUNTOS POR EL CAMBIO CHUBUT'),
    ('JUSTICIALISTA'),
    ('LA NEUQUINIDAD'),
    ('PARTIDO RENOVADOR FEDERAL'),
    ('PRIMERO LOS SALTEÑOS')
ON CONFLICT DO NOTHING;

-- Insert Coalitions
INSERT INTO Coalition (Name) VALUES 
    ('CONVICCIÓN FEDERAL'),
    ('DESPIERTA CHUBUT'),
    ('FRENTE CIVICO DE CORDOBA'),
    ('FRENTE CÍVICO POR SANTIAGO'),
    ('FRENTE PRO'),
    ('FRENTE RENOVADOR DE LA CONCORDIA SOCIAL'),
    ('INDEPENDENCIA'),
    ('JUSTICIALISTA'),
    ('LA LIBERTAD AVANZA'),
    ('LA NEUQUINIDAD'),
    ('MOVERE POR SANTA CRUZ'),
    ('PRIMERO LOS SALTEÑOS'),
    ('PROVINCIAS UNIDAS'),
    ('UCR - UNIÓN CÍVICA RADICAL')
ON CONFLICT DO NOTHING;