USE InternLink;
-- Add Admin Users
INSERT INTO `user` (username, full_name, email, password_hash, role, status) VALUES
('alice.admin', 'Alice Johnson', 'alice.johnson@internlink.com', '$2b$12$5WDknZAy4TG4xFSVu3dV..770dcC39pQvsIBbU56ksfmOIjQeWzdG', 'admin', 'active'),
('bob.admin', 'Bob Martinez', 'bob.martinez@internlink.com', '$2b$12$0Umi2ZQ4ssAI7YPQGMGndO7SLGmWE1AnYoUeyromW/NIlZuTh6X0S', 'admin', 'active');
-- ======================
-- 2. Add Employer Users
-- ======================
INSERT INTO `user` (username, full_name, email, password_hash, role, status) VALUES
('techcorp.hr', 'Emma Thompson', 'emma.thompson@techcorp.co.nz', '$2b$12$iFLeTQqhZEnLP7d8vhAKVOSanKYvxLrR9bYymbwJsARmx6xcCB8hS', 'employer', 'active'),
('healthcare.hr', 'James Brown', 'james.brown@healthcare.co.nz', '$2b$12$8GqtGK8tLLIexSDR4PjgOOZV9pYxbKn/8VGvCN84nptFR3ro6Dgf6', 'employer', 'active'),
('edusoft.hr', 'Sophia Taylor', 'sophia.taylor@edusoft.co.nz', '$2b$12$mnUMEThAU3tQJw.NqZCqy.WiesiST0QwNkZdyzkcAVR8Si7U79dou', 'employer', 'active'),
('greenenergy.hr', 'Oliver Wilson', 'oliver.wilson@greenenergy.co.nz', '$2b$12$nXyIR0ICnvaR8E0tznL9HOsnvd44CUwAQnbJXQr20N4EoplarZrke', 'employer', 'active'),
('agrifoods.hr', 'Liam White', 'liam.white@agrifoods.co.nz', '$2b$12$mpoqbhkMUseQGN73IGNR4O62wgE6lHZoH.0p5lfCpDo2p7CdFCw42', 'employer', 'active');

-- ======================
-- 3. Add Employers
-- ======================
INSERT INTO `employer` (user_id, company_name, company_description, website, logo_path) VALUES
(3, 'TechCorp Ltd', 'Specializing in AI, cloud solutions, and enterprise applications.', 'https://www.techcorp.co.nz', '/logos/techcorp.png'),
(4, 'HealthCare Inc', 'Leading provider of medical devices and digital health solutions.', 'https://www.healthcare.co.nz', '/logos/healthcare.png'),
(5, 'EduSoft', 'Developing innovative education management platforms for schools and universities.', 'https://www.edusoft.co.nz', '/logos/edusoft.png'),
(6, 'GreenEnergy', 'A renewable energy startup focusing on solar and wind power.', 'https://www.greenenergy.co.nz', '/logos/greenenergy.png'),
(7, 'AgriFoods', 'Providing sustainable food and agricultural products to global markets.', 'https://www.agrifoods.co.nz', '/logos/agrifoods.png');

-- ======================
-- 4. Add Student Users (20 students)
-- ======================
INSERT INTO `user` (username, full_name, email, password_hash, role, status) VALUES
('mia.williams', 'Mia Williams', 'mia.williams@otago.ac.nz', '$2b$12$QK9tG478/zVta.zclA3VM.Jy2apgUq9R71fk8XMgKgeHiSgNrx79O', 'student', 'active'),
('noah.johnson', 'Noah Johnson', 'noah.johnson@canterbury.ac.nz', '$2b$12$F7B4z45RN.epactqh5jaz.bMK7IoWncI3dQEmynyU0tJfUq4XHd3K', 'student', 'active'),
('ava.smith', 'Ava Smith', 'ava.smith@aucklanduni.ac.nz', '$2b$12$JGor9zf9ojAbOY.jVVGOvu1D9ByuF4E1XHfrsmC1RevGPa1T6U2q2', 'student', 'active'),
('jack.brown', 'Jack Brown', 'jack.brown@massey.ac.nz', '$2b$12$rXqEd9zFuo9d1zrpW0AmNurwEWxC9DmE35KRzT1EawpVDjF07ofGO', 'student', 'active'),
('olivia.jones', 'Olivia Jones', 'olivia.jones@otago.ac.nz', '$2b$12$XY.4wTpXvzfKzUFT.JdjUuKbJ7hGB.7cEzIjj6/BRst.Y8oGBYUiy', 'student', 'active'),
('william.davis', 'William Davis', 'william.davis@canterbury.ac.nz', '$2b$12$AS4kxbexYsIzVwp2tUxWwuNQfjrPhKnttOlJNgu3s0KIHdQq6DiIS', 'student', 'active'),
('isabella.miller', 'Isabella Miller', 'isabella.miller@waikato.ac.nz', '$2b$12$pgXC3QP2TMqln1zADLFCpeH/XKs8H4mHQCwyZn927vXxlGy/Bty4K', 'student', 'active'),
('lucas.wilson', 'Lucas Wilson', 'lucas.wilson@aucklanduni.ac.nz', '$2b$12$ltfeBppV4P/CoyZ0HLO9QeH1.lg9mFtpDzt3oPmYPHnScOaBC7PNi', 'student', 'active'),
('amelia.moore', 'Amelia Moore', 'amelia.moore@massey.ac.nz', '$2b$12$9NW86e0Zv/sgDn.4cRCVGub3cR5gG7EHwwvm7GTGvVOUi8M2B.ZlW', 'student', 'active'),
('elijah.taylor', 'Elijah Taylor', 'elijah.taylor@otago.ac.nz', '$2b$12$Hu8dDwagN6tGueIbNenpDuQMUS1RI2vn9y.hfs0ID.gj0dN5qKULK', 'student', 'active'),
('sophia.anderson', 'Sophia Anderson', 'sophia.anderson@canterbury.ac.nz', '$2b$12$MbWDU67jKJweadt.JhGlP.4AL8HocHg1D5ZDzqN4OoBD/wLn2d6PS', 'student', 'active'),
('james.thomas', 'James Thomas', 'james.thomas@waikato.ac.nz', '$2b$12$85dpqV0uqMM6K5gAobn3jOt0Qn7BK3IaVd35.qbfNiBFLli0zLrOa', 'student', 'active'),
('charlotte.jackson', 'Charlotte Jackson', 'charlotte.jackson@aucklanduni.ac.nz', '$2b$12$8cHTqY4eDPDjfXrMSugvOuAdoXTsDztVyE7fGB9zWPHoAGIQcXXua', 'student', 'active'),
('benjamin.white', 'Benjamin White', 'benjamin.white@massey.ac.nz', '$2b$12$tNn6KiM3KfxLjXQr5QLRBOBSS9qNgj9Z6qn11ts2AK8JBv3tUA7De', 'student', 'active'),
('harper.harris', 'Harper Harris', 'harper.harris@otago.ac.nz', '$2b$12$SHjvuD929hiNMFWilr3n4.USLc/WPC4oLMh8OdYEpwbmYfe0wM1xy', 'student', 'active'),
('henry.martin', 'Henry Martin', 'henry.martin@canterbury.ac.nz', '$2b$12$ZX16kwnmVpzlj9uNPFgyo.MfRbAcH/ewNhfZIWvXvRE8LM/Luttwi', 'student', 'active'),
('evelyn.thompson', 'Evelyn Thompson', 'evelyn.thompson@waikato.ac.nz', '$2b$12$zv7pGi/c8OSI9UZI/mLrvOIkIUK1DbfU/PTUDgWh9fABRd5RsZALa', 'student', 'active'),
('alexander.garcia', 'Alexander Garcia', 'alexander.garcia@aucklanduni.ac.nz', '$2b$12$LTi6.SZ80z6dofkHtz7Dke1YiYzbe3hEfFKF2afkUGKtE1u75/zca', 'student', 'active'),
('ella.martinez', 'Ella Martinez', 'ella.martinez@massey.ac.nz', '$2b$12$D1nS8Oaq/KvJBquQ20AfoevgvjcfiIhTYi0DHaAUY2xlIS4yNLt2.', 'student', 'active'),
('daniel.robinson', 'Daniel Robinson', 'daniel.robinson@otago.ac.nz', '$2b$12$8BRFe09uSHyH/YPeMx7tO.Yr1GH.gAisGVDI1Hbm5pAY/ShcOGNca', 'student', 'active');

-- ======================
-- 5. Add Students
-- ======================
INSERT INTO `student` (user_id, university, course, resume_path) VALUES
(8, 'University of Otago', 'Computer Science', '/resumes/mia_williams.pdf'),
(9, 'University of Canterbury', 'Information Systems', '/resumes/noah_johnson.pdf'),
(10, 'University of Auckland', 'Data Science', '/resumes/ava_smith.pdf'),
(11, 'Massey University', 'Software Engineering', '/resumes/jack_brown.pdf'),
(12, 'University of Otago', 'Biotechnology', '/resumes/olivia_jones.pdf'),
(13, 'University of Canterbury', 'Health Informatics', '/resumes/william_davis.pdf'),
(14, 'University of Waikato', 'Cybersecurity', '/resumes/isabella_miller.pdf'),
(15, 'University of Auckland', 'Business Analytics', '/resumes/lucas_wilson.pdf'),
(16, 'Massey University', 'Marketing', '/resumes/amelia_moore.pdf'),
(17, 'University of Otago', 'Artificial Intelligence', '/resumes/elijah_taylor.pdf'),
(18, 'University of Canterbury', 'Finance', '/resumes/sophia_anderson.pdf'),
(19, 'University of Waikato', 'Architecture', '/resumes/james_thomas.pdf'),
(20, 'University of Auckland', 'UX Design', '/resumes/charlotte_jackson.pdf'),
(21, 'Massey University', 'Agricultural Science', '/resumes/benjamin_white.pdf'),
(22, 'University of Otago', 'Chemistry', '/resumes/harper_harris.pdf'),
(23, 'University of Canterbury', 'Civil Engineering', '/resumes/henry_martin.pdf'),
(24, 'University of Waikato', 'Media Studies', '/resumes/evelyn_thompson.pdf'),
(25, 'University of Auckland', 'Robotics', '/resumes/alexander_garcia.pdf'),
(26, 'Massey University', 'Food Technology', '/resumes/ella_martinez.pdf'),
(27, 'University of Otago', 'Psychology', '/resumes/daniel_robinson.pdf');

-- ======================
-- 6. Add Internships (20)
-- ======================
INSERT INTO `internship` (company_id, title, description, location, duration, skills_required, deadline, stipend, number_of_opening, additonal_req) VALUES
(1, 'Software Developer Intern', 'Assist in developing and testing new web applications.', 'Auckland', '3 months', 'Python, Flask, Git', '2025-08-01', '$1000', 2, 'Basic coding experience required'),
(1, 'Frontend Developer Intern', 'Support frontend development team building responsive UIs.', 'Remote', '3 months', 'HTML, CSS, ReactJS', '2025-08-10', '$900', 1, 'Knowledge of JavaScript frameworks'),
(2, 'Healthcare Data Analyst Intern', 'Analyze healthcare datasets and prepare visual reports.', 'Christchurch', '6 months', 'SQL, PowerBI', '2025-09-01', '$1500', 1, 'Strong analytical skills'),
(3, 'Education Platform Support Intern', 'Provide technical support to education software users.', 'Wellington', '4 months', 'Customer service, SQL basics', '2025-07-30', '$800', 3, 'Good communication skills'),
(4, 'Renewable Energy Analyst Intern', 'Research and analyze renewable energy markets.', 'Hamilton', '6 months', 'Excel, Research methods', '2025-08-10', '$1200', 2, 'Knowledge of energy markets preferred'),
(5, 'Marketing Intern', 'Assist with social media campaigns for food products.', 'Napier', '3 months', 'Canva, Instagram Marketing', '2025-08-05', '$900', 2, 'Creative mindset'),
(1, 'Database Management Intern', 'Help maintain and improve company databases.', 'Auckland', '3 months', 'MySQL, Data modeling', '2025-08-15', '$1000', 1, 'Basic DB knowledge required'),
(2, 'Mobile App Development Intern', 'Support development of healthcare mobile apps.', 'Christchurch', '4 months', 'Flutter, Dart', '2025-08-20', '$1100', 1, 'Interest in mobile app development'),
(3, 'Business Analyst Intern', 'Conduct business process analysis for education clients.', 'Wellington', '4 months', 'Excel, PowerPoint', '2025-09-01', '$950', 2, 'Strong documentation skills'),
(4, 'Graphic Design Intern', 'Design marketing materials for renewable products.', 'Hamilton', '3 months', 'Photoshop, Illustrator', '2025-08-25', '$700', 1, 'Portfolio required'),
(5, 'Research Assistant Intern', 'Assist in agricultural research experiments.', 'Napier', '6 months', 'Lab experience preferred', '2025-08-12', '$1000', 1, NULL),
(1, 'DevOps Intern', 'Support CI/CD pipeline setup and automation.', 'Auckland', '3 months', 'Docker, Jenkins', '2025-08-18', '$1200', 2, 'Linux knowledge preferred'),
(2, 'HR Intern', 'Assist HR team in recruitment and onboarding.', 'Christchurch', '3 months', 'MS Office, Communication', '2025-08-22', '$850', 2, NULL),
(3, 'Sales Intern', 'Assist sales team with client outreach.', 'Wellington', '3 months', 'CRM tools, Excel', '2025-08-30', '$900', 1, NULL),
(4, 'Cybersecurity Intern', 'Assist security team with monitoring and testing.', 'Hamilton', '4 months', 'Security tools, Linux', '2025-08-28', '$1300', 1, 'Interest in cybersecurity'),
(5, 'Food Quality Intern', 'Assist in food quality testing and documentation.', 'Napier', '3 months', 'Food Safety Standards', '2025-08-19', '$950', 1, NULL),
(1, 'Machine Learning Intern', 'Support ML model training and evaluation.', 'Auckland', '4 months', 'Python, TensorFlow', '2025-08-21', '$1500', 2, 'Knowledge of ML basics'),
(2, 'Cloud Computing Intern', 'Assist with AWS infrastructure management.', 'Christchurch', '4 months', 'AWS, Linux', '2025-08-23', '$1400', 1, NULL),
(3, 'UX Design Intern', 'Assist UI/UX team in design research and prototyping.', 'Wellington', '3 months', 'Figma, Adobe XD', '2025-08-24', '$1000', 1, NULL),
(4, 'IoT Intern', 'Assist IoT team with device integration testing.', 'Hamilton', '4 months', 'Arduino, C programming', '2025-08-26', '$1100', 1, NULL);

-- ======================
-- 7. Add Applications (20)
-- ======================
INSERT INTO `application` (student_id, internship_id, status, feedback) VALUES
(1, 1, 'Pending', NULL),
(2, 1, 'Accepted', 'Strong coding skills'),
(3, 2, 'Rejected', 'Portfolio missing'),
(4, 3, 'Pending', NULL),
(5, 4, 'Pending', NULL),
(6, 5, 'Accepted', 'Excellent communication'),
(7, 6, 'Pending', NULL),
(8, 7, 'Pending', NULL),
(9, 8, 'Rejected', 'Insufficient experience'),
(10, 9, 'Pending', NULL),
(11, 10, 'Pending', NULL),
(12, 11, 'Pending', NULL),
(13, 12, 'Accepted', 'Quick learner'),
(14, 13, 'Rejected', 'Did not meet role criteria'),
(15, 14, 'Pending', NULL),
(16, 15, 'Pending', NULL),
(17, 16, 'Accepted', 'Very good technical knowledge'),
(18, 17, 'Pending', NULL),
(19, 18, 'Pending', NULL),
(20, 19, 'Pending', NULL);
