INSERT INTO package_name VALUES(225, 'kernel');
INSERT INTO evr VALUES(32, '0', '2.6.32', '696.20.1.el6', '(0,"{""(9,)"",""(6,)"",""(10,)"",""(-2,)""}","{""(1,)"",""(0,module)"",""(0,el)"",""(8,)"",""(2470,)"",""(0,
d)"",""(1,)"",""(0,bafa)"",""(0,)"",""(0,e)"",""(-2,)""}")');
INSERT INTO package VALUES(1, 225, 32, 20, 'Kernel for basic OS functions.', 'Kernel description', null);

INSERT INTO certificate VALUES (1, 'dummy_cert', 'lorem', 'ipsum', null);
INSERT INTO certificate VALUES (2, 'dummy_cert2', 'lorem', 'ipsum', null);

INSERT INTO product VALUES (2, 'Red Hat Enterprise Linux Server', null);
INSERT INTO content_set VALUES (42, 'rhel-6-server-rpms', 'Red Hat Enterprise Linux 6 Server (RPMs)', 2);
INSERT INTO repo VALUES (36, 'www.redhat.com', 42, 20, '696.20.1.el6', true, CURRENT_TIMESTAMP, 1);

INSERT INTO pkg_repo VALUES(1, 36);

INSERT INTO product VALUES (3, 'Red Hat Enterprise Linux Desktop', null);
INSERT INTO content_set VALUES (41, 'rhel-6-desktop-rpms', 'Red Hat Enterprise Linux 6 Desktop (RPMs)', 3);
INSERT INTO repo VALUES (37, 'www.redhat.com', 41, 20, '696.20.1.el6', true, CURRENT_TIMESTAMP, 2);

INSERT INTO pkg_repo VALUES(1, 37);