ALTER TABLE content_set
    ADD COLUMN IF NOT EXISTS
        third_party BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE module_stream
    ALTER
        COLUMN stream_name TYPE VARCHAR;

ALTER TABLE module_stream
    ALTER
        COLUMN context TYPE VARCHAR;