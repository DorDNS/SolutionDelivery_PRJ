import sqlite3

conn = sqlite3.connect("../backend/src/db.sqlite3")
cur = conn.cursor()

cur.execute("""
    INSERT INTO ClassificationConstraints (
        min_size, max_size,
        min_height, max_height,
        min_width, max_width,
        min_avg_r, max_avg_r,
        min_avg_g, max_avg_g,
        min_avg_b, max_avg_b,
        min_contrast, max_contrast,
        min_edges, max_edges
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    0.0, 5000.0,       # Size
    0, 5000,           # Height
    0, 5000,           # Width
    0.0, 255.0,        # Avg_R
    0.0, 255.0,        # Avg_G
    0.0, 255.0,        # Avg_B
    0.0, 1.0,          # Contrast_level
    0, 10000           # Edges
))

conn.commit()
conn.close()
