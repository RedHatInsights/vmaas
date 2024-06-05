ALTER TABLE csaf_product DROP CONSTRAINT pkg_id; 

WITH cte AS (
    SELECT cp.id as product_id, p.name_id FROM csaf_product cp JOIN package p ON cp.package_id = p.id
)
UPDATE csaf_product cp SET package_name_id = cte.name_id FROM cte WHERE cp.id = cte.product_id;

ALTER TABLE csaf_product ALTER COLUMN package_name_id SET NOT NULL;
