CREATE TYPE lp AS ENUM ('minor', 'eus', 'aus', 'e4s', 'els', 'tus');

ALTER TABLE operating_system ADD COLUMN lifecycle_phase lp;
UPDATE operating_system SET lifecycle_phase = 'minor';
ALTER TABLE operating_system ALTER COLUMN lifecycle_phase SET NOT NULL;
ALTER TABLE operating_system ADD CONSTRAINT operating_system_name_major_minor_lifecycle_phase_uq UNIQUE (name, major, minor, lifecycle_phase);
ALTER TABLE operating_system DROP CONSTRAINT operating_system_name_major_minor_uq;
