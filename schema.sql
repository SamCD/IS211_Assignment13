CREATE TABLE Students (ID INT PRIMARY KEY,
						firstName TEXT,
						lastName TEXT)
						
CREATE TABLE Quizzes (ID INT PRIMARY KEY,
						subject TEXT,
						questions INT,
						testDate date)
						
CREATE TABLE Results (ID INT PRIMARY KEY,
						quizID INT,
						studentID INT,
						grade float)
