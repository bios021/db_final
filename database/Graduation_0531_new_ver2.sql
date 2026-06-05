SET NAMES utf8mb4; -- 強制確保使用 UTF-8 編碼寫入
CREATE TABLE `STUDENTS` (
  `student_id` integer PRIMARY KEY,
  `student_name` varchar(20) NOT NULL,
  `password` varchar(20) NOT NULL COMMENT '登入系統所需密碼#hash過的字串
',
  `unit_id` integer NOT NULL COMMENT '  ',
  `enrollment_year` integer NOT NULL COMMENT '入學學年度
'
);

CREATE TABLE `COURSES` (
  `course_id` integer,
  `semester` integer,
  `course_name` varchar(50) NOT NULL,
  `subject_id` integer NOT NULL COMMENT '  ',
  `unit_id` integer NOT NULL COMMENT '  ',
  `credits` integer NOT NULL COMMENT '學分數
',
  PRIMARY KEY (`course_id`, `semester`)
);

CREATE TABLE `STD_COURSE_HISTORY` (
  `student_id` integer,
  `course_id` integer,
  `semester` integer COMMENT '在哪個學期修的課。eg.1121代表112學年第一學期
',
  `grade` integer COMMENT '成績
',
  PRIMARY KEY (`student_id`, `course_id`, `semester`)
);

CREATE TABLE `UNITS` (
  `unit_id` integer PRIMARY KEY COMMENT '  ',
  `unit_name` varchar(20) NOT NULL,
  `college_id` integer COMMENT '該單位所屬院所(或是所屬上級單位)
'
);

CREATE TABLE `RULE` (
  `rule_id` integer PRIMARY KEY AUTO_INCREMENT,
  `rule_name` varchar(40) NOT NULL,
  `unit_id` integer NOT NULL COMMENT '  ',
  `enrollment_year` integer NOT NULL COMMENT '規則適用於哪一學年入學的學生
',
  `required_credits` integer NOT NULL COMMENT '  '
);

CREATE TABLE `CONDITION` (
  `condition_id` integer PRIMARY KEY AUTO_INCREMENT,
  `condition_name` varchar(50) NOT NULL,
  `rule_id` integer NOT NULL,
  `required_credits` integer NOT NULL,
  `max_admitted_credits` integer NOT NULL
);

CREATE TABLE `CONDITION_COURSE` (
  `condition_id` integer,
  `course_id` integer,
  `semester` integer,
  PRIMARY KEY (`condition_id`, `course_id`, `semester`)
);

CREATE TABLE `SUBJECT` (
  `subject_id` integer PRIMARY KEY AUTO_INCREMENT,
  `subject_name` varchar(50) NOT NULL
);

ALTER TABLE `STUDENTS` COMMENT = '學生
';

ALTER TABLE `COURSES` COMMENT = '開設過的課程
';

ALTER TABLE `STD_COURSE_HISTORY` COMMENT = '學生修課紀錄(學生與課程的關聯)
';

ALTER TABLE `UNITS` COMMENT = '單位，範圍包含系所、院所、通識中心等等
';

ALTER TABLE `RULE` COMMENT = '規則。ex.112學年入學資訊系必修規則(要求50學分)、111年統計系通識及體育規則(要求32學分)。
';

ALTER TABLE `CONDITION` COMMENT = '某規則下要求修的課程類別。ex. 微積分甲、群C、人文通、社會核通。人文通識要求至少三學分，超過七學分不認列；微積分甲科目要求修六學分，修超過六學分不認列；統計系群C要求修兩門課(等價於修六學分)，修超過的部分認列為選修學分。
';

ALTER TABLE `CONDITION_COURSE` COMMENT = '課程類別與課程的關聯。ex. 那些課程屬於統計系微積分甲這個課程類別。那些課程屬於人文通識；那些課程屬於統計系群C。
';

ALTER TABLE `SUBJECT` COMMENT = '那些課程屬於同一個科目(除學年課外修習相同科目不計入學分)
';

ALTER TABLE `STD_COURSE_HISTORY` ADD CONSTRAINT `taken1` FOREIGN KEY (`student_id`) REFERENCES `STUDENTS` (`student_id`);

ALTER TABLE `STD_COURSE_HISTORY` ADD CONSTRAINT `taken2` FOREIGN KEY (`course_id`, `semester`) REFERENCES `COURSES` (`course_id`, `semester`);

ALTER TABLE `STUDENTS` ADD CONSTRAINT `MAJOR` FOREIGN KEY (`unit_id`) REFERENCES `UNITS` (`unit_id`);

ALTER TABLE `UNITS` ADD CONSTRAINT `BELONG` FOREIGN KEY (`college_id`) REFERENCES `UNITS` (`unit_id`);

ALTER TABLE `COURSES` ADD CONSTRAINT `OPEN` FOREIGN KEY (`unit_id`) REFERENCES `UNITS` (`unit_id`);

ALTER TABLE `RULE` ADD FOREIGN KEY (`unit_id`) REFERENCES `UNITS` (`unit_id`);

ALTER TABLE `CONDITION` ADD FOREIGN KEY (`rule_id`) REFERENCES `RULE` (`rule_id`);

ALTER TABLE `CONDITION_COURSE` ADD FOREIGN KEY (`course_id`, `semester`) REFERENCES `COURSES` (`course_id`, `semester`);

ALTER TABLE `CONDITION_COURSE` ADD FOREIGN KEY (`condition_id`) REFERENCES `CONDITION` (`condition_id`);

ALTER TABLE `COURSES` ADD FOREIGN KEY (`subject_id`) REFERENCES `SUBJECT` (`subject_id`);

-- 以下為系統預設資料
-- 1. units
-- 學院
INSERT INTO `UNITS` (`unit_id`, `unit_name`, `college_id`) VALUES 
(1, '資訊學院', NULL),
(2, '商學院', NULL);

-- 系所，綁定對應的學院
INSERT INTO `UNITS` (`unit_id`, `unit_name`, `college_id`) VALUES 
(11, '資訊科學系', 1),
(12, '統計學系', 2);

-- ==========================================
-- 2. 建立科目大類 (SUBJECT)
-- 用途：定義核心科目，避免不同學期開的同名/相似課程重複採計
-- ==========================================
INSERT INTO `SUBJECT` (`subject_id`, `subject_name`) VALUES 
-- 資科系
(101, '微積分甲'),
(102, '計算機程式設計(一)'),
(103, '計算機程式設計(二)'),
(104, '線性代數'),
(105, '物件導向程式設計(一)'),
-- 統計系
(201, '統計學(一)'),
(202, '統計學(二)'),
(203, '經濟學');
-- 待新增

-- ==========================================
-- 3. 建立畢業規則大綱 (RULE)
-- ==========================================
INSERT INTO `RULE` (`rule_id`, `rule_name`, `unit_id`, `enrollment_year`, `required_credits`) VALUES 
(1, '111學年度資訊科學系專業必修規則', 11, 111, 39),
(2, '111學年度資訊科學系專業群修規則', 11, 111, 12),
(11, '111學年度統計學系專業必修規則', 12, 111, 42),
(12, '111學年度統計學系專業群修規則', 12, 111, 9),
(99, '111學年度資訊科學系通識規則', 11, 111, 28); -- 由於規則綁定系所、學年，同樣的通識規則需要許多筆資料，或許學年、系所不用設 not null


-- 4. CONDITION 建立規則底下的學分門檻 
INSERT INTO `CONDITION` (`condition_id`, `rule_id`, `condition_name`, `required_credits`,`max_admitted_credits`) VALUES 
-- 通識
(1, 99, '111資科人文通', 3, 7),
(2, 99, '111資科社會通', 3, 7),
(3, 99, '111資科自然通', 3, 7), -- 同樣因為通識規則綁定學年、科系、需排列組合
(11, 2, '111學年度資訊科學系群修A', 6, 6),
(12, 2, '111學年度資訊科學系群修B', 3 ,3),
(13, 2, '111學年度資訊科學系群修C', 3 ,3),
(21, 12, '111學年度統計系群修四選二', 6, 6),
(22, 12, '111學年度統計系群修八選一', 3 ,3);



-- 5. COURSES (建立學期真實開課)
-- 匯入 1121 學期 統計學課程
INSERT IGNORE INTO `COURSES` (`course_id`, `semester`, `course_name`, `subject_id`, `unit_id`, `credits`) VALUES 
('000359021', 1121, '統計學（一）', 201, 12, 3),
('000359031', 1121, '統計學（一）', 201, 12, 3),
('000359041', 1121, '統計學（一）', 201, 12, 3),
('000359061', 1121, '統計學（一）', 201, 12, 3),
('000359071', 1121, '統計學（一）', 201, 12, 3),
('000359201', 1121, '統計學（一）', 201, 12, 3),
('000359221', 1121, '統計學（一）', 201, 12, 3),
('000359051', 1121, '統計學（一）', 201, 12, 3),
('000359081', 1121, '統計學（一）', 201, 12, 3),
('000359211', 1121, '統計學（一）', 201, 12, 3);
-- ('ZU1014001', 1121, '統計學（一）', 201, NULL, 3); -- 創國學院開課 課號非INT 可能要改varchar

-- 6. CONDITION_COURSE (把課程丟進對應的籃子)
-- INSERT INTO `CONDITION_COURSE` (`condition_id`, `course_id`, `semester`) VALUES 
-- (11, '???', 1121), -- 屬於資科系群修A
-- (12, '???', 1121), -- 屬於資科系群修B
-- (13, '???', 1121); -- 屬於資科系群修C
-- 待新增
 

-- 7. 建立測試學生 (STUDENTS)
INSERT INTO `STUDENTS` (`student_id`, `student_name`, `password`, `unit_id`, `enrollment_year`) VALUES 
(112304099, '王曉明', 'password123', 2, 112);

-- 8. 建立修課紀錄 (STD_COURSE_HISTORY)
INSERT INTO `STD_COURSE_HISTORY` (`student_id`, `course_id`, `semester`, `grade`) VALUES 
(112304099, 000359021, 1121, 85); -- 統計學(一) (過關)