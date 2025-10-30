DELETE FROM csaf_cve_product
USING csaf_product
WHERE csaf_cve_product.csaf_product_id = csaf_product.id
  AND csaf_product.variant_suffix = 'N/A'
  AND csaf_product.package_id IS NULL;


DELETE FROM csaf_product
WHERE variant_suffix = 'N/A'
  AND package_id IS NULL;