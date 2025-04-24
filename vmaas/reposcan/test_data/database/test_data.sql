DELETE FROM errata_cve;
DELETE FROM cve;
DELETE FROM pkg_errata;
DELETE FROM module_stream_require;
DELETE FROM module_stream;
DELETE FROM module;
DELETE FROM errata_repo;
DELETE FROM pkg_repo;
DELETE FROM repo;
DELETE FROM certificate;
DELETE FROM content_set;
DELETE FROM product;
DELETE FROM errata;
DELETE FROM errata_type;
DELETE FROM package;
DELETE FROM evr;
DELETE FROM package_name;

INSERT INTO package_name (id, name) VALUES
  (101, 'pkg-sec-errata1'),
  (102, 'pkg-no-sec-errata2'),
  (103, 'pkg-errata-cve3'),
  (104, 'pkg-sec-errata4');

INSERT INTO evr (id, epoch, version, release, evr) VALUES
  (201, '1', '1', '1', ('1', ARRAY[(1,null)::evr_array_item], ARRAY[(1,null)::evr_array_item])),
  (202, '1', '1', '2', ('1', ARRAY[(1,null)::evr_array_item], ARRAY[(2,null)::evr_array_item])),
  (203, '1', '1', '3', ('1', ARRAY[(1,null)::evr_array_item], ARRAY[(3,null)::evr_array_item])),
  (204, '2', '2', '2', ('2', ARRAY[(2,null)::evr_array_item], ARRAY[(2,null)::evr_array_item])),
  (205, '3', '3', '3', ('3', ARRAY[(3,null)::evr_array_item], ARRAY[(3,null)::evr_array_item])),
  (206, '4', '4', '4', ('4', ARRAY[(4,null)::evr_array_item], ARRAY[(4,null)::evr_array_item]));

INSERT INTO package (id, name_id, evr_id, arch_id, summary, description, source_package_id) VALUES
  (301, 101, 201, 1, 'summary1', 'description1', null),
  (302, 101, 202, 1, 'summary1', 'description1', null),
  (303, 101, 203, 1, 'summary1', 'description1', 301),
  (304, 102, 204, 1, 'summary2', 'description2', 301),
  (305, 103, 205, 1, 'summary3', 'description3', 301),
  (306, 103, 206, 1, 'summary3', 'description3', 302),
  (307, 104, 204, 1, 'summary4', 'description4', 302);

INSERT INTO errata_type (id, name) VALUES
  (1, 'security'),
  (2, 'bug');

INSERT INTO errata (id, name, synopsis, severity_id, errata_type_id, summary, description, solution, issued, updated) VALUES
  (401, 'errata1', 'synopsis1', 4, 1, 'summary1', 'description1', 'solution1', '2019-01-01 01:00:00-05', '2019-01-01 02:00:22-05'),
  (402, 'errata2', 'synopsis2', 4, 2, 'summary2', 'description2', 'solution2', '2019-02-01 01:00:00-05', '2019-02-02 01:00:00-05'),
  (403, 'errata3', 'synopsis3', 4, 2, 'summary3', 'description3', 'solution3', '2019-03-01 01:00:00-05', '2019-03-03 01:00:00-05');

INSERT INTO product (id, name, redhat_eng_product_id) VALUES
  (501, 'product1', 1),
  (502, 'product2', 2);

INSERT INTO content_set (id, label, name, product_id) VALUES
  (601, 'content set 1', 'content-set-name-1', 501),
  (602, 'content set 2', 'content-set-name-2', 502);

INSERT INTO certificate (id, name, ca_cert, cert, key) VALUES
  (701, 'certificate-name-1', 'ca_cert_1', 'cert1', 'key1'),
  (702, 'certificate-name-2', 'ca_cert_2', 'cert2', 'key2');

INSERT INTO repo (id, url, content_set_id, basearch_id, releasever, eol, revision, certificate_id, org_id) VALUES
  (801, 'https://www.repourl.com/repo1', 601, 1, '1', true, '2019-08-01 01:00:00-05', 701, 1),
  (802, 'https://www.repourl.com/repo2', 602, 1, '1', true, '2019-08-02 01:00:00-05', 702, 1);

INSERT INTO pkg_repo (pkg_id, repo_id) VALUES
  (301, 801),
  (302, 801),
  (303, 801),
  (304, 801),
  (305, 801),
  (306, 801),
  (306, 802),
  (307, 802);

INSERT INTO errata_repo (errata_id, repo_id) VALUES
  (401, 801),
  (402, 801),
  (403, 801),
  (401, 802);

INSERT INTO module (id, name, repo_id, arch_id) VALUES
  (1001, 'module1', 801, 1),
  (1002, 'module2', 802, 1);

INSERT INTO module_stream (id, module_id, stream_name, version, context, is_default) VALUES
  (1101, 1001, 'stream1', 11, 'fun1', true),
  (1102, 1002, 'stream2', 12, 'fun2', true),
  (1103, 1001, 'stream1', 13, 'fun3', false);

INSERT INTO module_stream_require (module_stream_id, require_id) VALUES
  (1102, 1103);

INSERT INTO pkg_errata (pkg_id, errata_id, module_stream_id) VALUES
  (301, 401, 1101),
  (301, 403, null),
  (302, 401, 1103),
  (304, 402, null),
  (305, 403, null),
  (306, 403, null),
  (307, 401, 1102);

INSERT INTO cve (id, name, description, impact_id, published_date, modified_date, cvss3_score, cvss3_metrics, iava, redhat_url, secondary_url, source_id, cvss2_score, cvss2_metrics) VALUES
  (901, 'CVE-0000-0001', 'cvedesc1', 6, '2019-09-01 02:00:00-05', '2019-09-01 02:02:00-05', 1.111, 'cvss3-1.111', 'iava1', 'http://cve.redhat.com/1', 'http://secondary.redhat.com/1', 1, 1.112, 'cvss2-1.112');

INSERT INTO errata_cve (errata_id, cve_id) VALUES
  (403, 901);
