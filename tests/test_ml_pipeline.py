import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai_job_dashboard.ml.skill_extraction import extract_skills_from_text
from ai_job_dashboard.ml.skill_gap import skill_gap
from ai_job_dashboard.ml.salary_predictor import build_features

class TestMLPipeline(unittest.TestCase):
    def test_skill_extraction(self):
        text = "Seeking a Senior Software Engineer with strong Python, SQL, and Docker experience."
        skills = extract_skills_from_text(text)
        self.assertIn("python", skills)
        self.assertIn("sql", skills)
        self.assertIn("docker", skills)

    def test_skill_gap_analysis(self):
        resume = "Experienced in Python, Pandas, and NumPy for data manipulation."
        job_spec = "Required: Python, Pandas, Docker, Kubernetes, AWS."
        gap = skill_gap(resume, job_spec)

        self.assertIn("docker", gap["missing"])
        self.assertIn("kubernetes", gap["missing"])
        self.assertIn("python", gap["resume_skills"])
        self.assertIn("numpy", gap["extra"])

    def test_build_features_for_salary(self):
        sample_jobs = [
            {
                "title": "Machine Learning Engineer",
                "description": "Building computer vision pipelines",
                "company": "AI Labs",
                "location": "Remote",
                "skills": ["python", "pytorch"],
                "experience": "3+ years",
                "salary_min": 120000,
                "salary_max": 160000
            }
        ]
        rows, y = build_features(sample_jobs)
        self.assertEqual(len(rows), 1)
        self.assertEqual(len(y), 1)
        self.assertEqual(y[0], 140000.0)

if __name__ == '__main__':
    unittest.main()
