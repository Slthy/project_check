PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE roles(
    rnumber INT,
    rtitle VARCHAR(50),
    PRIMARY KEY(rnumber)
);
INSERT INTO roles VALUES(0,'Applicant');
INSERT INTO roles VALUES(1,'Student');
INSERT INTO roles VALUES(2,'Faculty Reviewer');
INSERT INTO roles VALUES(3,'GS');
INSERT INTO roles VALUES(4,'CAC');
INSERT INTO roles VALUES(5,'Admin');
CREATE TABLE users (
    user_id VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(50),
    role_id INT NOT NULL,
    PRIMARY KEY(user_id),
    FOREIGN KEY(role_id) REFERENCES roles(rnumber)
);
INSERT INTO users VALUES('gs1','gs1@gwu.edu','scrypt:32768:8:1$hcYx5gpgo4kG0VK4$8ef29d8860b14e488342c4fffb32680f2b7f7733a54cbe0919762fb674a352396ad0838a854edabe6ccc60a5eb6c675aa1297886bf4e33cecac4fa445cae8595',3);
INSERT INTO users VALUES('cac1','cac1@gwu.edu','scrypt:32768:8:1$SAcLHI58aZfoV6Nb$f1d43f4d1190b3b8d52c6fc78a4ce593690717023d1487583203f2cc68c690c80273f46f954a359343753c1249d425f6cfa8e9c6c5390ffb566cdc4b31eed3ce',4);
INSERT INTO users VALUES('Admin1','Admin1@gwu.edu','scrypt:32768:8:1$FAQzkRwgVPyVAu4H$c6c223bf8cf5360eca5bc140e229d7ef0725e9dcac97b85777f5d098ddb7c026060b0779a6bd6b58b625a54bc036b0cab18c415599eb0ccf77129e47b4951f90',5);
INSERT INTO users VALUES('prof_cs1','prof_cs1@gwu.edu','scrypt:32768:8:1$fXaNuBMYYrDkVE4p$40f63bf60abc16ab153ee6110878c4f390a8d9f8549ccc5f12888f57d2d4427e87f9983cd5a8a865d86af1dca7d97752dbb69d017cee82451aec0482af64b8dc',2);
INSERT INTO users VALUES('prof_ece1','prof_ece1@gwu.edu','scrypt:32768:8:1$UmZQNFItTV4dpkxV$69138900b636870ab40027afab9fa21c9db5360d9999636190e2d2e5ec735823579525b237724077bf1ab6c3f8472853e9777dce2bbbecdb6b081753a5d52952',2);
INSERT INTO users VALUES('prof_bme1','prof_bme1@gwu.edu','scrypt:32768:8:1$sHmUFoTCJExlIuhv$d75702082ca2ac8927ce0922972d980322870e8ef3bc6f0226bafd41da2190e6eb761da0a534fda9074350ca5ac15552309c2d783503c1a882613b4b184d4212',2);
INSERT INTO users VALUES('prof_ce1','prof_ce1@gwu.edu','scrypt:32768:8:1$C4cxp7Q5RmHTVXuT$eccae145e41bc778f4c9862dc6dcfa09c477e4341834bc0536a87e19f548ea35f9bc2d9060c4ee33ec401b2c8728838fc43d906d4b008346550bd87beb75a86c',2);
INSERT INTO users VALUES('prof_mce1','prof_mce1@gwu.edu','scrypt:32768:8:1$3wD1kjIZtZxDTZ6B$70838abd6b94b3ff03f24494f73a2365675c7219c77e1b54f98aef78dc391791c5b89b94775ffae3a08b79a7b46135f5533ee7d7afb557389a7b2896062b2f8b',2);
INSERT INTO users VALUES('testID','testID@gmail.com','scrypt:32768:8:1$C078d5cUwbK1WEyB$b66e078426c2d753701e9a3ee8441bd41e6eec2464d0deb0827fc01f3ad7dc6db82cf601bd9e2db8a7b300e0e539cdc0004da13a62067dcda52bf13a1042f515',0);
INSERT INTO users VALUES('arvin','arvin@gmail.com','scrypt:32768:8:1$la0ttrlYXsgtxNll$965254a3519f41e8edf4fba378c2b390b0d7edddf10e161538c0180a6856335f8ef81386502c98062ea8dc11e368887341af05d08f0de8c8349488a857694ef6',0);
INSERT INTO users VALUES('asd','asd@asd','scrypt:32768:8:1$JNgvZ4G8BBpuELUG$68b0a4a034a28020766874ff6e0bb0e94b0c2f4bbfa1f8270fbd71f3720147c2ab7fe434cab6fc7040e369188f00ab1ffde8eaafc233dbb8b38016f5a148e417',0);
INSERT INTO users VALUES('student_Ua7fbe5f3','student_Ua7fbe5f3@gwu.edu','scrypt:32768:8:1$pXMZ5mdvdlOZClyk$b2c752f507105aa7efdebc6e6697e389a43c8c5eb553ea738eeda17ec97f179416b6273d1aeb08da9d0576e0981795c495c2d3a2cb5a96240bbf922abdbf555b',1);
INSERT INTO users VALUES('qwe','qwe@qwe','scrypt:32768:8:1$JoDjYvEnCas4YfMh$acf6501ef241ba45a036f450c234dc5355c57cbc9a3621cbb1047e1175da02676138f46ab67e4e2ad1939b42b6dd58f1c1686d4166c2d8ccae1050bce6fce7e9',0);
INSERT INTO users VALUES('student_U-019d4a03-816c-74a8-aaa7-4a6c3d385b75','student_U-019d4a03-816c-74a8-aaa7-4a6c3d385b75@gwu.edu','scrypt:32768:8:1$ght9WAid03qLuZnE$6845b0a6d61d9a0c778ec70819d76c180fd020c0ea9d2a9d6dca0fbc0325238d61810cd64a12406a88a7e942e5fda6f7464a3b5b6a15b61ef38f02c42ed6496d',1);
INSERT INTO users VALUES('qqq','qqq@qqq','scrypt:32768:8:1$fqys21KtZyk97Nak$ec6cca909d55b6d36190bd4f91e289fe43a87f24b9b824d76ae6af1e0a7a3e66448c9af98ec97cb613e4288cca8c309499e97cf6ea5d3f09202964ed68ec5942',0);
INSERT INTO users VALUES('zxc','zxc@zxc','scrypt:32768:8:1$fCi9J2PMGAhFZJzu$c38df0e651238f9a00689b232eba64cf9dac202bc42509f55d91ee2e6f0d016c447c044b3d92136227a7cd21dc736fa39df46c7c6e58cc0913e88672161eb232',0);
CREATE TABLE departments(
    dnumber INT,
    dname VARCHAR(50) NOT NULL,
    PRIMARY KEY(dnumber)
);
INSERT INTO departments VALUES(1,'Engineering');
CREATE TABLE programs(
    pnumber INT,
    pname   VARCHAR(50) NOT NULL,
    dno INT NOT NULL,
    PRIMARY KEY(pnumber),
    FOREIGN KEY(dno) REFERENCES departments(dnumber)
);
INSERT INTO programs VALUES(101,'CS',1);
INSERT INTO programs VALUES(102,'ECE',1);
INSERT INTO programs VALUES(103,'BME',1);
INSERT INTO programs VALUES(104,'CE',1);
INSERT INTO programs VALUES(105,'MCE',1);
CREATE TABLE applicants(
    uid VARCHAR(50),
    user_id VARCHAR(50) NOT NULL UNIQUE,
    fname VARCHAR(50) NOT NULL,
    lname VARCHAR(50) NOT NULL,
    address VARCHAR(100),
    dob DATE,
    ssn VARCHAR(9),
    PRIMARY KEY(uid),
    FOREIGN kEY(user_id) REFERENCES users(user_id)
);
INSERT INTO applicants VALUES('00000001','arvin','arvin','sarsazi','2026 Wisconsin Ave, Washington, DC','1999-07-21','333445555');
INSERT INTO applicants VALUES('00000002','mohab','mohab','elshabasy','2028 Wisconsin Ave, Washington, DC','1999-02-21','111445555');
INSERT INTO applicants VALUES('Ua7fbe5f3','asd','asd','asd','asdasd','2011-03-17','222222223');
INSERT INTO applicants VALUES('U-019d4a03-816c-74a8-aaa7-4a6c3d385b75','qwe','qwe','qwe','qweqwe','2010-12-09','454545454');
CREATE TABLE faculty (
    user_id VARCHAR(50),
    fname VARCHAR(50) NOT NULL,
    lname VARCHAR(50) NOT NULL,
    dno INT NOT NULL,
    PRIMARY KEY(user_id),
    FOREIGN kEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(dno) REFERENCES departments(dnumber)
);
INSERT INTO faculty VALUES('prof_cs1','Gabe','Parmer',1);
INSERT INTO faculty VALUES('prof_ece1','Thomas','Edison',1);
INSERT INTO faculty VALUES('prof_bme1','Charles','Darwin',1);
INSERT INTO faculty VALUES('prof_ce1','Bridge','Skycraper',1);
INSERT INTO faculty VALUES('prof_mce1','Stephen','Hawking',1);
INSERT INTO faculty VALUES('cac1','Grace','Hopper',1);
CREATE TABLE soughtdeg( 
    deg_no INT,
    deg_type VARCHAR(50),
    PRIMARY KEY(deg_no)
);
INSERT INTO soughtdeg VALUES(1,'MS');
INSERT INTO soughtdeg VALUES(2,'PHD');
CREATE TABLE applications(
    app_id VARCHAR(50),
    uid VARCHAR(50) NOT NULL,
    deg_no INT NOT NULL,
    pro_no INT NOT NULL,
    semester VARCHAR(50) NOT NULL,
    app_year INT NOT NULL,
    status VARCHAR(50) NOT NULL,
    final_dec VARCHAR(50),
    toefl_score INT,
    toefl_exam_year INT,
    areas_of_interest VARCHAR(200),
    PRIMARY KEY(app_id),
    FOREIGN KEY(uid) REFERENCES applicants(uid),
    FOREIGN KEY(deg_no) REFERENCES soughtdeg(deg_no),
    FOREIGN KEY(pro_no) REFERENCES programs(pnumber)
);
INSERT INTO applications VALUES('APP001','00000001',2,101,'Fall',2026,'Decision Made','Admit with Aid',110,2023,'Machine Learning');
INSERT INTO applications VALUES('APP002','00000002',2,101,'Fall',2026,'Complete',NULL,NULL,NULL,'Artificial Intelligance');
INSERT INTO applications VALUES('A809d20d9','Ua7fbe5f3',1,101,'Fall',2027,'Decision Made','Admit with Aid',NULL,NULL,NULL);
INSERT INTO applications VALUES('A-019d4a03-816c-74a8-aaa7-4a6d14d32db0','U-019d4a03-816c-74a8-aaa7-4a6c3d385b75',1,104,'Fall',2027,'Decision Made','Admit with Aid',100,2026,'AI');
CREATE TABLE workex(
    wid VARCHAr(50),
    app_id VARCHAR(50) NOT NULL,
    job_title VARCHAR(50),
    description TEXT,
    com_name VARCHAR(50),
    man_name VARCHAR(50),
    man_email VARCHAR(50),
    man_number VARCHAR(50),
    start_date DATE,
    end_date DATE,
    PRIMARY KEY(wid),
    FOREIGN KEY(app_id) REFERENCES applications(app_id)
);
CREATE TABLE previous_deg(
    deg_id VARCHAr(50),
    app_id VARCHAR(50) NOT NULL,
    dtype VARCHAR(50),
    dyear INT,
    dGPA DECIMAL(3,2),
    duni VARCHAR(50),
    dmajor VARCHAR(50),
    PRIMARY KEY(deg_id),
    FOREIGN KEY(app_id) REFERENCES applications(app_id)
);
INSERT INTO previous_deg VALUES('D001','APP001','BS',2020,2.850000000000000088,'George Washington University','Computer Science');
INSERT INTO previous_deg VALUES('D002','APP001','MS',2025,3.399999999999999912,'Stanford University','Computer Science');
INSERT INTO previous_deg VALUES('D003','APP002','BS',2021,3.850000000000000088,'George Washington University','Computer Science');
INSERT INTO previous_deg VALUES('D8719785b','A809d20d9','BS',1950,3.209999999999999965,'GWU','CS');
INSERT INTO previous_deg VALUES('D-019d4a03-816d-765f-a367-0ee8234d5cd8','A-019d4a03-816c-74a8-aaa7-4a6d14d32db0','BS',1950,3.419999999999999929,'asd','BME');
CREATE TABLE recommendation(
    rid VARCHAr(50),
    app_id VARCHAR(50) NOT NULL,
    rfname VARCHAR(50),
    rlname VARCHAR(50),
    remail VARCHAR(50),
    rnumber VARCHAR(50),
    raffiliation VARCHAR(50),
    rtitle VARCHAR(50),
    submitted BOOLEAN DEFAULT FALSE,
    submitted_date Date,
    letter_text TEXT,
    letter_rating INT,
    is_generic BOOLEAN,
    is_credible BOOLEAN,
    PRIMARY KEY(rid),
    FOREIGN KEY(app_id) REFERENCES applications(app_id)
);
INSERT INTO recommendation VALUES('R001','APP001','Reza','Malek','rmm@gwu.edu',NULL,'George Washington University','Professor',1,NULL,NULL,3,0,1);
INSERT INTO recommendation VALUES('R002','APP002','Reza','Malek','rmm@gwu.edu',NULL,'George Washington University','Professor',1,NULL,NULL,NULL,NULL,NULL);
INSERT INTO recommendation VALUES('R4b203d03','A809d20d9','Reza','Malek','r.m@mm','','GWU','Professor',1,'2026-04-01','He''s nice',3,1,1);
INSERT INTO recommendation VALUES('R-019d4a03-816e-76b2-9c68-ee3ff7a766ef','A-019d4a03-816c-74a8-aaa7-4a6d14d32db0','asda','asdasd','asd@asd','','asdas','asdasd',0,NULL,NULL,3,1,0);
INSERT INTO recommendation VALUES('R-019d4a03-816e-76b2-9c68-ee40177bb9cc','A-019d4a03-816c-74a8-aaa7-4a6d14d32db0','qwe','assd','zxcxzc@sad','','was','wades',1,'2026-04-01','asdjsandkasjnc',2,0,0);
CREATE TABLE transcripts(
    trans_id VARCHAR(50),
    app_id VARCHAR(50) NOT NULL,
    received BOOLEAN DEFAULT FALSE,
    received_date DATE,
    PRIMARY KEY(trans_id),
    FOREIGN KEY(app_id) REFERENCES applications(app_id)
);
INSERT INTO transcripts VALUES('T001','APP001',1,'2025-12-10');
INSERT INTO transcripts VALUES('T30c9a8a2','A809d20d9',1,'2026-04-01');
INSERT INTO transcripts VALUES('T-019d4a03-816e-76b2-9c68-ee410c194934','A-019d4a03-816c-74a8-aaa7-4a6d14d32db0',1,'2026-04-01');
CREATE TABLE gre(
    gid VARCHAR(50),
    app_id VARCHAR(50) NOT NULL,
    verbal INT,
    quantitative INT,
    total INT,
    subj_score INT,
    subj_name VARCHAR(50),
    exam_year INT,
    PRIMARY KEY(gid),
    FOREIGN KEY(app_id) REFERENCES applications(app_id)
);
INSERT INTO gre VALUES('G001','APP001',160,168,328,NULL,NULL,2025);
INSERT INTO gre VALUES('G65c14c3f','A809d20d9',134,159,293,400,'Real',2018);
INSERT INTO gre VALUES('G-019d4a03-816f-760f-829e-f1ecb40399a5','A-019d4a03-816c-74a8-aaa7-4a6d14d32db0',140,150,290,400,'AQQ',2021);
CREATE TABLE review(
    review_id VARCHAR(50),
    app_id VARCHAR(50) NOT NULL,
    reviewer_id VARCHAR(50) NOT NULL,
    rating INT,
    recom_advisor_id VARCHAR(50),
    comments VARCHAR(200),
    reject_reason VARCHAR(100),
    deficiency_courses VARCHAR(100),
    final_recommendation VARCHAR(100),
    PRIMARY KEY(review_id),
    FOREIGN KEY(app_id) REFERENCES applications(app_id),
    FOREIGN KEY (recom_advisor_id) REFERENCES faculty(user_id),
    FOREIGN KEY(reviewer_id) REFERENCES faculty(user_id)
);
INSERT INTO review VALUES('REV001','APP001','prof_cs1',4,'prof_cs1','Strong problem solving skills',NULL,NULL,'Admit with Aid');
INSERT INTO review VALUES('REV002','A809d20d9','prof_cs1',2,'prof_bme1','None','','None',NULL);
INSERT INTO review VALUES('REV003','A809d20d9','prof_ece1',3,'prof_bme1','None','','None',NULL);
INSERT INTO review VALUES('REV004','A-019d4a03-816c-74a8-aaa7-4a6d14d32db0','prof_ce1',2,'prof_ece1','None','','None',NULL);
CREATE TABLE students(
    uid VARCHAR(50),
    user_id VARCHAR(50) UNIQUE,
    admit_app_id VARCHAR(50) UNIQUE,
    start_semester VARCHAR(50),
    start_year INT,
    PRIMARY KEY(uid),
    FOREIGN KEY(uid) REFERENCES applicants(uid),
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(admit_app_id) REFERENCES applications(app_id)
);
INSERT INTO students VALUES('00000001','arvin','APP001','Fall',2026);
INSERT INTO students VALUES('Ua7fbe5f3','student_Ua7fbe5f3','A809d20d9','Fall',2027);
INSERT INTO students VALUES('U-019d4a03-816c-74a8-aaa7-4a6c3d385b75','student_U-019d4a03-816c-74a8-aaa7-4a6c3d385b75','A-019d4a03-816c-74a8-aaa7-4a6d14d32db0','Fall',2027);
COMMIT;
