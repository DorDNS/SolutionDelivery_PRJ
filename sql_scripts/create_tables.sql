CREATE TABLE Image(
   Id_Image INT PRIMARY KEY,
   File_name VARCHAR(120) NOT NULL,
   File_path VARCHAR(500) NOT NULL,
   Size FLOAT NOT NULL,
   Height INT NOT NULL,
   Width INT NOT NULL,
   Date_taken DATE,
   Avg_R FLOAT,
   Avg_G FLOAT,
   Avg_B FLOAT,
   Contrast_level FLOAT,
   RGB_Histogram JSON,
   Luminance_Histogram JSON,
   Edges INT,
   Status BOOLEAN,
   Status_CondIA BOOLEAN,
   Status_DeepIA BOOLEAN,
   UNIQUE(File_name),
   UNIQUE(File_path)
);

CREATE TABLE Location(
   Id_Location INT PRIMARY KEY,
   Latitude FLOAT,
   Longitude FLOAT,
   City VARCHAR(50),
   Id_Image INT NOT NULL,
   FOREIGN KEY(Id_Image) REFERENCES Image(Id_Image)
);

CREATE TABLE ClassificationConstraints (
   id INTEGER PRIMARY KEY AUTOINCREMENT,
   feature VARCHAR(64),
   operator VARCHAR(16),
   threshold INT,
   SCORE FLOAT
);

INSERT INTO ClassificationConstraints (feature, operator, threshold, SCORE) VALUES
('Size', '>', 500, 0.26),
('Avg_B', '>', 85, 0.115),
('Contrast_level', '>', 50, 0.5),
('Edges', '>', 65000, 0.29),
('Max_Blue_Index', '>', 200, 0.12);
