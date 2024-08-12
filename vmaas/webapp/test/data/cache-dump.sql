BEGIN TRANSACTION;
CREATE TABLE arch (
                                id integer primary key,
                                arch text
                               );
INSERT INTO "arch" VALUES(1,'noarch');
INSERT INTO "arch" VALUES(2,'i386');
INSERT INTO "arch" VALUES(3,'i486');
INSERT INTO "arch" VALUES(4,'i586');
INSERT INTO "arch" VALUES(5,'i686');
INSERT INTO "arch" VALUES(6,'alpha');
INSERT INTO "arch" VALUES(7,'alphaev6');
INSERT INTO "arch" VALUES(8,'ia64');
INSERT INTO "arch" VALUES(9,'sparc');
INSERT INTO "arch" VALUES(10,'sparcv9');
INSERT INTO "arch" VALUES(11,'sparc64');
INSERT INTO "arch" VALUES(12,'s390');
INSERT INTO "arch" VALUES(13,'athlon');
INSERT INTO "arch" VALUES(14,'s390x');
INSERT INTO "arch" VALUES(15,'ppc');
INSERT INTO "arch" VALUES(16,'ppc64');
INSERT INTO "arch" VALUES(17,'ppc64le');
INSERT INTO "arch" VALUES(18,'pSeries');
INSERT INTO "arch" VALUES(19,'iSeries');
INSERT INTO "arch" VALUES(20,'x86_64');
INSERT INTO "arch" VALUES(21,'ppc64iseries');
INSERT INTO "arch" VALUES(22,'ppc64pseries');
INSERT INTO "arch" VALUES(23,'ia32e');
INSERT INTO "arch" VALUES(24,'amd64');
INSERT INTO "arch" VALUES(25,'aarch64');
INSERT INTO "arch" VALUES(26,'armv7hnl');
INSERT INTO "arch" VALUES(27,'armv7hl');
INSERT INTO "arch" VALUES(28,'armv7l');
INSERT INTO "arch" VALUES(29,'armv6hl');
INSERT INTO "arch" VALUES(30,'armv6l');
INSERT INTO "arch" VALUES(31,'armv5tel');
INSERT INTO "arch" VALUES(32,'src');
CREATE TABLE arch_compat (
                                from_arch_id integer,
                                to_arch_id integer
                               );
INSERT INTO "arch_compat" VALUES(1,1);
INSERT INTO "arch_compat" VALUES(2,1);
INSERT INTO "arch_compat" VALUES(2,2);
INSERT INTO "arch_compat" VALUES(1,2);
INSERT INTO "arch_compat" VALUES(3,1);
INSERT INTO "arch_compat" VALUES(3,3);
INSERT INTO "arch_compat" VALUES(1,3);
INSERT INTO "arch_compat" VALUES(4,1);
INSERT INTO "arch_compat" VALUES(4,4);
INSERT INTO "arch_compat" VALUES(1,4);
INSERT INTO "arch_compat" VALUES(5,1);
INSERT INTO "arch_compat" VALUES(5,5);
INSERT INTO "arch_compat" VALUES(1,5);
INSERT INTO "arch_compat" VALUES(6,1);
INSERT INTO "arch_compat" VALUES(6,6);
INSERT INTO "arch_compat" VALUES(1,6);
INSERT INTO "arch_compat" VALUES(7,1);
INSERT INTO "arch_compat" VALUES(7,7);
INSERT INTO "arch_compat" VALUES(1,7);
INSERT INTO "arch_compat" VALUES(8,1);
INSERT INTO "arch_compat" VALUES(8,8);
INSERT INTO "arch_compat" VALUES(1,8);
INSERT INTO "arch_compat" VALUES(9,1);
INSERT INTO "arch_compat" VALUES(9,9);
INSERT INTO "arch_compat" VALUES(1,9);
INSERT INTO "arch_compat" VALUES(10,1);
INSERT INTO "arch_compat" VALUES(10,10);
INSERT INTO "arch_compat" VALUES(1,10);
INSERT INTO "arch_compat" VALUES(11,1);
INSERT INTO "arch_compat" VALUES(11,11);
INSERT INTO "arch_compat" VALUES(1,11);
INSERT INTO "arch_compat" VALUES(12,1);
INSERT INTO "arch_compat" VALUES(12,12);
INSERT INTO "arch_compat" VALUES(1,12);
INSERT INTO "arch_compat" VALUES(13,1);
INSERT INTO "arch_compat" VALUES(13,13);
INSERT INTO "arch_compat" VALUES(1,13);
INSERT INTO "arch_compat" VALUES(14,1);
INSERT INTO "arch_compat" VALUES(14,14);
INSERT INTO "arch_compat" VALUES(1,14);
INSERT INTO "arch_compat" VALUES(15,1);
INSERT INTO "arch_compat" VALUES(15,15);
INSERT INTO "arch_compat" VALUES(1,15);
INSERT INTO "arch_compat" VALUES(16,1);
INSERT INTO "arch_compat" VALUES(16,16);
INSERT INTO "arch_compat" VALUES(1,17);
INSERT INTO "arch_compat" VALUES(17,17);
INSERT INTO "arch_compat" VALUES(17,1);
INSERT INTO "arch_compat" VALUES(1,16);
INSERT INTO "arch_compat" VALUES(20,1);
INSERT INTO "arch_compat" VALUES(20,20);
INSERT INTO "arch_compat" VALUES(1,20);
INSERT INTO "arch_compat" VALUES(21,1);
INSERT INTO "arch_compat" VALUES(21,21);
INSERT INTO "arch_compat" VALUES(1,21);
INSERT INTO "arch_compat" VALUES(22,1);
INSERT INTO "arch_compat" VALUES(22,22);
INSERT INTO "arch_compat" VALUES(1,22);
INSERT INTO "arch_compat" VALUES(1,28);
INSERT INTO "arch_compat" VALUES(28,28);
INSERT INTO "arch_compat" VALUES(28,1);
INSERT INTO "arch_compat" VALUES(1,29);
INSERT INTO "arch_compat" VALUES(29,29);
INSERT INTO "arch_compat" VALUES(29,1);
INSERT INTO "arch_compat" VALUES(1,30);
INSERT INTO "arch_compat" VALUES(30,30);
INSERT INTO "arch_compat" VALUES(30,1);
INSERT INTO "arch_compat" VALUES(1,31);
INSERT INTO "arch_compat" VALUES(31,31);
INSERT INTO "arch_compat" VALUES(31,1);
INSERT INTO "arch_compat" VALUES(1,27);
INSERT INTO "arch_compat" VALUES(27,27);
INSERT INTO "arch_compat" VALUES(27,1);
INSERT INTO "arch_compat" VALUES(1,26);
INSERT INTO "arch_compat" VALUES(26,26);
INSERT INTO "arch_compat" VALUES(26,1);
INSERT INTO "arch_compat" VALUES(1,25);
INSERT INTO "arch_compat" VALUES(25,25);
INSERT INTO "arch_compat" VALUES(25,1);
INSERT INTO "arch_compat" VALUES(24,1);
INSERT INTO "arch_compat" VALUES(24,24);
INSERT INTO "arch_compat" VALUES(1,24);
CREATE TABLE content_set (
                  id integer primary key not null,
                  label text not null check ( label <> '' )
            );
INSERT INTO "content_set" VALUES(601,'content set 1');
INSERT INTO "content_set" VALUES(602,'content set 2');
CREATE TABLE content_set_pkg_name (
                 content_set_id integer not null,
                 pkg_name_id integer not null,
                 primary key (content_set_id, pkg_name_id)
           );
INSERT INTO "content_set_pkg_name" VALUES(602,103);
INSERT INTO "content_set_pkg_name" VALUES(601,103);
INSERT INTO "content_set_pkg_name" VALUES(601,102);
INSERT INTO "content_set_pkg_name" VALUES(602,104);
INSERT INTO "content_set_pkg_name" VALUES(601,101);
CREATE TABLE content_set_src_pkg_name (
                content_set_id integer not null,
                src_pkg_name_id integer not null,
                primary key (content_set_id, src_pkg_name_id)
            );
INSERT INTO "content_set_src_pkg_name" VALUES(602,101);
INSERT INTO "content_set_src_pkg_name" VALUES(601,101);
CREATE TABLE cpe (
                id integer primary key  not null ,
                label text unique not null check ( label <> '' )
            );
CREATE TABLE cpe_content_set(
                cpe_id integer not null,
                content_set_id integer not null,
                primary key (cpe_id, content_set_id)
            );
CREATE TABLE cve_cwe (
                                cve_id integer,
                                cwe text
                               );
CREATE TABLE cve_detail (
                                id integer primary key ,
                                name text,
                                redhat_url text,
                                secondary_url text,
                                cvss3_score float,
                                cvss3_metrics text,
                                impact text,
                                published_date text,
                                modified_date text,
                                iava text,
                                description text,
                                cvss2_score float,
                                cvss2_metrics text,
                                source text
                               );
INSERT INTO "cve_detail" VALUES(901,'CVE-0000-0001','http://cve.redhat.com/1','http://secondary.redhat.com/1',1.111,'cvss3-1.111','High','2019-09-01T07:00:00+00:00','2019-09-01T07:02:00+00:00','iava1','cvedesc1',1.112,'cvss2-1.112','Red Hat');
CREATE TABLE cve_pkg (
                                cve_id integer,
                                pkg_id integer
                               );
INSERT INTO "cve_pkg" VALUES(901,301);
INSERT INTO "cve_pkg" VALUES(901,305);
INSERT INTO "cve_pkg" VALUES(901,306);
CREATE TABLE dbchange (
                                errata_changes text,
                                cve_changes text,
                                repository_changes text,
                                last_change text,
                                exported text
                               );
INSERT INTO "dbchange" VALUES('2021-10-25T12:23:49.442257+00:00','2021-10-25T12:23:49.442257+00:00','2021-10-25T12:23:49.442257+00:00','2021-10-25T12:23:49.442257+00:00','1635164630.10132');
CREATE TABLE errata_bugzilla (
                                errata_id integer,
                                bugzilla text
                               );
CREATE TABLE errata_cve (
                                errata_id integer,
                                cve text,
                                primary key(errata_id, cve)
                               ) without rowid;
INSERT INTO "errata_cve" VALUES(403,'CVE-0000-0001');
CREATE TABLE errata_detail (
                                id integer primary key,
                                name text,
                                synopsis text,
                                summary text,
                                type text,
                                severity text,
                                description text,
                                solution text,
                                issued text,
                                updated text,
                                url text,
                                third_party integer,
                                requires_reboot boolean
                               );
INSERT INTO "errata_detail" VALUES(401,'errata1','synopsis1','summary1','security','Important','description1','solution1','2019-01-01T06:00:00+00:00','2019-01-01T07:00:22+00:00','https://access.redhat.com/errata/errata1',0,1);
INSERT INTO "errata_detail" VALUES(402,'errata2','synopsis2','summary2','bug','Important','description2','solution2','2019-02-01T06:00:00+00:00','2019-02-02T06:00:00+00:00','https://access.redhat.com/errata/errata2',0,1);
INSERT INTO "errata_detail" VALUES(403,'errata3','synopsis3','summary3','bug','Important','description3','solution3','2019-03-01T06:00:00+00:00','2019-03-03T06:00:00+00:00','https://access.redhat.com/errata/errata3',0,1);
CREATE TABLE errata_module (
                                errata_id integer,
                                module_name text,
                                module_stream_id integer,
                                module_stream text,
                                module_version integer,
                                module_context text
                               );
INSERT INTO "errata_module" VALUES(401,'module2',1102,'stream2',12,'fun2');
INSERT INTO "errata_module" VALUES(401,'module1',1103,'stream1',13,'fun3');
INSERT INTO "errata_module" VALUES(401,'module1',1101,'stream1',11,'fun1');
CREATE TABLE errata_modulepkg (
                                errata_id integer,
                                module_stream_id integer,
                                pkg_id integer,
                                primary key(errata_id, module_stream_id, pkg_id)
                               );
INSERT INTO "errata_modulepkg" VALUES(401,1103,302);
INSERT INTO "errata_modulepkg" VALUES(401,1101,301);
INSERT INTO "errata_modulepkg" VALUES(401,1102,307);
CREATE TABLE errata_refs (
                                errata_id integer,
                                ref text
                               );
CREATE TABLE errata_repo (
                                errata_id integer,
                                repo_id integer,
                                primary key(errata_id, repo_id)
                                ) without rowid;
INSERT INTO "errata_repo" VALUES(401,801);
INSERT INTO "errata_repo" VALUES(401,802);
INSERT INTO "errata_repo" VALUES(402,801);
INSERT INTO "errata_repo" VALUES(403,801);
CREATE TABLE evr (
                                id integer primary key,
                                epoch integer,
                                version text,
                                release text
                                );
INSERT INTO "evr" VALUES(201,1,'1','1');
INSERT INTO "evr" VALUES(202,1,'1','2');
INSERT INTO "evr" VALUES(203,1,'1','3');
INSERT INTO "evr" VALUES(204,2,'2','2');
INSERT INTO "evr" VALUES(205,3,'3','3');
INSERT INTO "evr" VALUES(206,4,'4','4');
CREATE TABLE module_stream (
                                stream_id integer,
                                module text,
                                stream text
                               );
INSERT INTO "module_stream" VALUES(1101,'module1','stream1');
INSERT INTO "module_stream" VALUES(1103,'module1','stream1');
INSERT INTO "module_stream" VALUES(1102,'module2','stream2');
CREATE TABLE module_stream_require (
                                stream_id integer,
                                require_id integer
                               );
INSERT INTO "module_stream_require" VALUES(1102,1103);
CREATE TABLE package_detail (
                                id integer primary key,
                                name_id integer,
                                evr_id integer,
                                arch_id integer,
                                summary_id integer,
                                description_id integer,
                                source_package_id integer,
                                modified timestamp
                               );
INSERT INTO "package_detail" VALUES(301,101,201,1,3415031729060068275,6666926469049561356,NULL,'2021-10-25 12:23:49.442257');
INSERT INTO "package_detail" VALUES(302,101,202,1,3415031729060068275,6666926469049561356,NULL,'2021-10-25 12:23:49.442257');
INSERT INTO "package_detail" VALUES(303,101,203,1,3415031729060068275,6666926469049561356,301,'2021-10-25 12:23:49.442257');
INSERT INTO "package_detail" VALUES(304,102,204,1,4630564460918104136,1018050409587461006,301,'2021-10-25 12:23:49.442257');
INSERT INTO "package_detail" VALUES(305,103,205,1,-5977099973117524146,8492286707935751597,301,'2021-10-25 12:23:49.442257');
INSERT INTO "package_detail" VALUES(306,103,206,1,-5977099973117524146,8492286707935751597,302,'2021-10-25 12:23:49.442257');
INSERT INTO "package_detail" VALUES(307,104,204,1,-1598543113460573933,359499587181539707,302,'2021-10-25 12:23:49.442257');
CREATE TABLE packagename (
                                id integer primary key,
                                packagename text
                                );
INSERT INTO "packagename" VALUES(101,'pkg-sec-errata1');
INSERT INTO "packagename" VALUES(102,'pkg-no-sec-errata2');
INSERT INTO "packagename" VALUES(103,'pkg-errata-cve3');
INSERT INTO "packagename" VALUES(104,'pkg-sec-errata4');
CREATE TABLE pkg_errata (
                                pkg_id integer,
                                errata_id integer,
                                primary key (pkg_id, errata_id)
                                ) without rowid;
INSERT INTO "pkg_errata" VALUES(301,401);
INSERT INTO "pkg_errata" VALUES(301,403);
INSERT INTO "pkg_errata" VALUES(302,401);
INSERT INTO "pkg_errata" VALUES(304,402);
INSERT INTO "pkg_errata" VALUES(305,403);
INSERT INTO "pkg_errata" VALUES(306,403);
INSERT INTO "pkg_errata" VALUES(307,401);
CREATE TABLE pkg_repo (
                                pkg_id integer,
                                repo_id integer,
                                primary key (pkg_id, repo_id)
                               ) without rowid;
INSERT INTO "pkg_repo" VALUES(301,801);
INSERT INTO "pkg_repo" VALUES(302,801);
INSERT INTO "pkg_repo" VALUES(303,801);
INSERT INTO "pkg_repo" VALUES(304,801);
INSERT INTO "pkg_repo" VALUES(305,801);
INSERT INTO "pkg_repo" VALUES(306,801);
INSERT INTO "pkg_repo" VALUES(306,802);
INSERT INTO "pkg_repo" VALUES(307,802);
CREATE TABLE repo_detail (
                                id integer primary key,
                                label text,
                                name text,
                                url text,
                                basearch text,
                                releasever text,
                                product text,
                                product_id integer,
                                revision text,
                                last_change text,
                                third_party integer
                               );
INSERT INTO "repo_detail" VALUES(801,'content set 1','content-set-name-1','https://www.repourl.com/repo1/','noarch','1','product1',501,'2019-08-01T06:00:00+00:00','2019-08-01T06:00:00+00:00',0);
INSERT INTO "repo_detail" VALUES(802,'content set 2','content-set-name-2','https://www.repourl.com/repo2/','noarch','1','product2',502,'2019-08-02T06:00:00+00:00','2019-08-02T06:00:00+00:00',0);
CREATE TABLE string (
                                id integer primary key,
                                string text
                               );
INSERT INTO "string" VALUES(-5977099973117524146,'summary3');
INSERT INTO "string" VALUES(-1598543113460573933,'summary4');
INSERT INTO "string" VALUES(359499587181539707,'description4');
INSERT INTO "string" VALUES(1018050409587461006,'description2');
INSERT INTO "string" VALUES(3415031729060068275,'summary1');
INSERT INTO "string" VALUES(4630564460918104136,'summary2');
INSERT INTO "string" VALUES(6666926469049561356,'description1');
INSERT INTO "string" VALUES(8492286707935751597,'description3');
CREATE TABLE updates (
                                    name_id integer,
                                    package_id integer,
                                    package_order integer
                                );
INSERT INTO "updates" VALUES(101,301,0);
INSERT INTO "updates" VALUES(101,302,1);
INSERT INTO "updates" VALUES(101,303,2);
INSERT INTO "updates" VALUES(102,304,0);
INSERT INTO "updates" VALUES(103,305,0);
INSERT INTO "updates" VALUES(103,306,1);
INSERT INTO "updates" VALUES(104,307,0);
CREATE TABLE updates_index (
                                    name_id integer,
                                    evr_id integer,
                                    package_order integer
                                    );
INSERT INTO "updates_index" VALUES(101,201,0);
INSERT INTO "updates_index" VALUES(101,202,1);
INSERT INTO "updates_index" VALUES(101,203,2);
INSERT INTO "updates_index" VALUES(102,204,0);
INSERT INTO "updates_index" VALUES(103,205,0);
INSERT INTO "updates_index" VALUES(103,206,1);
INSERT INTO "updates_index" VALUES(104,204,0);
COMMIT;
