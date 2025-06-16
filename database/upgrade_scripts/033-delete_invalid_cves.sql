DELETE FROM cve_cwe
USING cve
WHERE cve_cwe.cve_id = cve.id
  AND cve.published_date IS NULL
  AND cve.modified_date IS NULL;

DELETE FROM errata_cve
USING cve
WHERE errata_cve.cve_id = cve.id
  AND cve.published_date IS NULL
  AND cve.modified_date IS NULL;

DELETE FROM csaf_cve_product
USING cve
WHERE csaf_cve_product.cve_id = cve.id
  AND cve.published_date IS NULL
  AND cve.modified_date IS NULL;

DELETE FROM cve WHERE published_date IS NULL AND modified_date IS NULL;
