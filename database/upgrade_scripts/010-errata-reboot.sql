ALTER TABLE errata
    ADD COLUMN IF NOT EXISTS requires_reboot BOOLEAN NOT NULL
        DEFAULT TRUE;