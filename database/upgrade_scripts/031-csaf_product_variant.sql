ALTER TABLE csaf_product ADD COLUMN variant_suffix TEXT NOT NULL CHECK (NOT empty(variant_suffix)) DEFAULT 'N/A';

DROP INDEX csaf_product_cpe_id_package_name_id_idx;
DROP INDEX csaf_product_cpe_id_package_name_id_module_stream_idx;
DROP INDEX csaf_product_cpe_id_package_name_id_package_id_idx;
DROP INDEX csaf_product_cpe_id_package_name_id_package_id_module_strea_idx;

CREATE UNIQUE INDEX ON csaf_product(cpe_id, variant_suffix, package_name_id) WHERE package_name_id IS NOT NULL AND package_id IS NULL AND module_stream IS NULL;
CREATE UNIQUE INDEX ON csaf_product(cpe_id, variant_suffix, package_name_id, module_stream) WHERE package_name_id IS NOT NULL AND package_id IS NULL AND module_stream IS NOT NULL;
CREATE UNIQUE INDEX ON csaf_product(cpe_id, variant_suffix, package_name_id, package_id) WHERE package_name_id IS NOT NULL and package_id IS NOT NULL AND module_stream IS NULL;
CREATE UNIQUE INDEX ON csaf_product(cpe_id, variant_suffix, package_name_id, package_id, module_stream) WHERE package_name_id IS NOT NULL and package_id IS NOT NULL AND module_stream IS NOT NULL;
