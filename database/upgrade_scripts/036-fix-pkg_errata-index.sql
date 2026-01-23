CREATE UNIQUE INDEX pkg_errata_pkgid_errataid_streamid ON pkg_errata (pkg_id, errata_id, module_stream_id)
WHERE module_stream_id IS NOT NULL;
DROP INDEX pkg_errata_pkgid_streamid_errataid;
