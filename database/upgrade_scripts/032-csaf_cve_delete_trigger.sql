create or replace FUNCTION delete_unreferenced_csaf_products()
  RETURNS TRIGGER AS
$delete_unreferenced_csaf_products$
  BEGIN
    DELETE FROM csaf_product p
    WHERE p.id = OLD.csaf_product_id
      AND NOT EXISTS (
        SELECT 1 FROM csaf_cve_product c
        WHERE c.csaf_product_id = p.id
      );
    RETURN NULL;
  END;
$delete_unreferenced_csaf_products$
  LANGUAGE 'plpgsql';

CREATE TRIGGER csaf_cve_deleted AFTER DELETE ON csaf_cve_product
  FOR EACH ROW
  EXECUTE FUNCTION delete_unreferenced_csaf_products();
