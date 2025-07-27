-- -----------------------------------------------------
-- Schema internlink
-- -----------------------------------------------------
create database internlink;
use internlink;
-- -----------------------------------------------------
-- Table `user`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `user` (
  `user_id` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(50) NOT NULL,
  `full_name` VARCHAR(100) NULL DEFAULT NULL,
  `email` VARCHAR(100) NOT NULL,
  `password_hash` CHAR(60) CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_bin' NOT NULL,
  `profile_image` VARCHAR(255) NULL DEFAULT NULL,
  `role` ENUM('student', 'employer', 'admin') NOT NULL DEFAULT 'student',
  `status` ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
  PRIMARY KEY (`user_id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;
-- -----------------------------------------------------
-- Table `student`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `student` (
  `student_id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `university` VARCHAR(100) NULL DEFAULT NULL,
  `course` VARCHAR(100) NULL DEFAULT NULL,
  `resume_path` VARCHAR(255) NULL DEFAULT NULL,
  PRIMARY KEY (`student_id`),
  UNIQUE INDEX `user_id` (`user_id` ASC) VISIBLE,
  CONSTRAINT `student_ibfk_1`
    FOREIGN KEY (`user_id`)
    REFERENCES `user` (`user_id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;
-- -----------------------------------------------------
-- Table `employer`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `employer` (
  `emp_id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `company_name` VARCHAR(100) NOT NULL,
  `company_description` TEXT NULL DEFAULT NULL,
  `website` VARCHAR(100) NULL DEFAULT NULL,
  `logo_path` VARCHAR(255) NULL DEFAULT NULL,
  PRIMARY KEY (`emp_id`),
  UNIQUE INDEX `user_id` (`user_id` ASC) VISIBLE,
  CONSTRAINT `employer_ibfk_1`
    FOREIGN KEY (`user_id`)
    REFERENCES `user` (`user_id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `internship`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `internship` (
  `internship_id` INT NOT NULL AUTO_INCREMENT,
  `company_id` INT NOT NULL,
  `title` VARCHAR(100) NOT NULL,
  `description` TEXT NOT NULL,
  `location` VARCHAR(100) NULL DEFAULT NULL,
  `duration` VARCHAR(50) NULL DEFAULT NULL,
  `skills_required` TEXT NULL DEFAULT NULL,
  `deadline` DATE,
  `stipend` VARCHAR(50) NULL DEFAULT NULL,
  `number_of_opening` INT,
  `additonal_req` TEXT NULL DEFAULT NULL,
  PRIMARY KEY (`internship_id`),
  CONSTRAINT `internship_ibfk_1`
    FOREIGN KEY (`company_id`)
    REFERENCES `employer` (`emp_id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `application`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `application` (
  `student_id` INT NOT NULL,
  `internship_id` INT NOT NULL,
  `status` ENUM('Pending', 'Accepted', 'Rejected') NULL DEFAULT 'Pending',
  `feedback` TEXT NULL DEFAULT NULL,
  PRIMARY KEY (`student_id`, `internship_id`),
  INDEX `internship_id` (`internship_id` ASC) VISIBLE,
  CONSTRAINT `application_ibfk_1`
    FOREIGN KEY (`student_id`)
    REFERENCES `student` (`student_id`),
  CONSTRAINT `application_ibfk_2`
    FOREIGN KEY (`internship_id`)
    REFERENCES `internship` (`internship_id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
