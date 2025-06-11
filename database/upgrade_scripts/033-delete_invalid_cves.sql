DO $$ 
BEGIN
    WITH wrong_cve_id AS (
        SELECT id from cve where name = 'cve-2022-28693'
    ), correct_cve_id AS (
        SELECT id from cve where name = 'CVE-2022-28693'
    )

    -- link the one incorrect cve being linked to csaf_cve_product
    update csaf_cve_product
        set cve_id = (select id from correct_cve_id)
        where cve_id = (select id from wrong_cve_id);
END $$;

-- delete all wrong cves
delete from cve where published_date is null and modified_date is null;
