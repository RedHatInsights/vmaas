ALTER TABLE csaf_products ADD CONSTRAINT unique_csaf_product UNIQUE (cpe, package, module);
ALTER TABLE csaf_cves ADD CONSTRAINT unique_csaf_cve_product UNIQUE (cve, csaf_product_id);
