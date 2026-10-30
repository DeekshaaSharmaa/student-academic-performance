# generate_data.py
# Creates a SYNTHETIC (fake, anonymous) student dataset for practice.

import os
import numpy as np
import pandas as pd

np.random.seed(42)          # same random numbers every run, so results are repeatable
n = 200                     # number of students

# --- Basic columns ---
df = pd.DataFrame({
    "Student_ID": [f"S{str(i).zfill(3)}" for i in range(1, n + 1)],
    "Gender": np.random.choice(["Male", "Female"], n),
    "Section": np.random.choice(["A", "B", "C"], n),
    # normal() gives bell-curve values; clip() keeps them in a sensible range
    "Attendance_Percent": np.clip(np.random.normal(75, 12, n), 40, 100).round(1),
    "Study_Hours_Per_Week": np.clip(np.random.normal(10, 4, n), 1, 30).round(1),
})

# --- Subject marks ---
# Marks depend a little on attendance and study hours, plus random noise.
# The number next to each subject makes that subject slightly easier/harder.
subjects = {
    "Mathematics": -3,
    "Python_Programming": 2,
    "Computer_Fundamentals": 6,
    "English": 3,
    "Statistics": -6,
}
for subject, offset in subjects.items():
    noise = np.random.normal(0, 8, n)
    marks = 15 + 0.35 * df["Attendance_Percent"] + 1.2 * df["Study_Hours_Per_Week"] + offset + noise
    df[subject] = np.clip(marks, 0, 100).round(0)

# --- Add realistic "mess" for the cleaning step ---
df.loc[[5, 23, 47, 88, 120], "Mathematics"] = np.nan        # missing marks
df.loc[[12, 77, 150], "Statistics"] = np.nan
df.loc[[30, 95], "Study_Hours_Per_Week"] = np.nan
df.loc[[3, 17, 60], "Gender"] = ["male", "F", "FEMALE"]      # inconsistent text
df.loc[10, "Attendance_Percent"] = 105                       # invalid value
df = pd.concat([df, df.sample(5, random_state=1)])           # 5 duplicate rows

# --- Save ---
os.makedirs("data/raw", exist_ok=True)
df.to_csv("data/raw/student_performance_raw.csv", index=False)
print("Saved! Shape:", df.shape)