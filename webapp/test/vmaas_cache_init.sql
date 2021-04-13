CREATE TABLE id2packagename (
    id INTEGER PRIMARY KEY,
    name TEXT
);

CREATE TABLE updates (
    pkgname_id INTEGER,
    arch_id INTEGER,
    pkg_ids INTEGER[],
    PRIMARY KEY (pkgname_id, arch_id)
);

CREATE TABLE id2arch (
    id INTEGER PRIMARY KEY,
    name TEXT
);

CREATE TABLE errataid2name (
    id INTEGER PRIMARY KEY,
    name TEXT
);
