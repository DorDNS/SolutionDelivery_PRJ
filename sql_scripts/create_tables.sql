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
