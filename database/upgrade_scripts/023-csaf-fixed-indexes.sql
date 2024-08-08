DROP INDEX IF EXISTS csaf_product_cpe_id_package_id_idx;
DROP INDEX IF EXISTS csaf_product_cpe_id_package_id_module_stream_idx;
CREATE UNIQUE INDEX ON csaf_product(cpe_id, package_name_id, package_id) WHERE package_name_id IS NOT NULL and package_id IS NOT NULL AND module_stream IS NULL;
CREATE UNIQUE INDEX ON csaf_product(cpe_id, package_name_id, package_id, module_stream) WHERE package_name_id IS NOT NULL and package_id IS NOT NULL AND module_stream IS NOT NULL;
