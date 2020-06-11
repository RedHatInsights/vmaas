ALTER TABLE errata_severity ALTER COLUMN name DROP NOT NULL;

UPDATE errata_severity SET name = NULL WHERE id = 1;
