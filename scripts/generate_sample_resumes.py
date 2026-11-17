import os
import pymupdf

def create_sample_pdf(file_path: str, content: str):
    """Generate a clean searchable PDF resume using PyMuPDF."""
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842) # A4 size

    # Margin and layout
    rect = pymupdf.Rect(50, 50, 545, 792)
    page.insert_textbox(rect, content, fontsize=10, fontname="helv", color=(0.1, 0.15, 0.2))

    doc.save(file_path)
    doc.close()

def generate_all_samples(output_dir: str = "./uploads/sample_resumes"):
    os.makedirs(output_dir, exist_ok=True)

    samples = [
        {
            "filename": "Alex_Rivera_FullStack.pdf",
            "content": """Alex Rivera
Email: alex.rivera@example.com | Phone: (555) 234-5678 | Location: San Francisco, CA
LinkedIn: linkedin.com/in/alexrivera-dev | GitHub: github.com/alexrivera

PROFESSIONAL SUMMARY
Senior Full Stack Software Engineer with 6+ years of experience designing and scaling web microservices and enterprise SaaS applications. Proficient in Python, FastAPI, React, PostgreSQL, and AWS cloud infrastructure.

TECHNICAL SKILLS
• Programming Languages: Python, JavaScript, TypeScript, SQL, Bash
• Web & Frontend: React, React.js, Next.js, Redux, Tailwind CSS, HTML5, CSS3
• Backend Frameworks: FastAPI, Django, Flask, Node.js, REST API, GraphQL
• Databases & Caching: PostgreSQL, Redis, SQLAlchemy, MongoDB
• Cloud & DevOps: Docker, AWS, Kubernetes, GitHub Actions, Linux, CI/CD
• Methodologies: Agile, Scrum, Microservices, System Design, Code Review

WORK EXPERIENCE
Senior Full Stack Developer | Apex Cloud Technologies (2021 - Present)
• Architected high-throughput REST APIs and microservices using FastAPI, PostgreSQL, and Redis.
• Built responsive client-facing web dashboards using React, TypeScript, and Tailwind CSS.
• Containerized services using Docker and orchestrated Kubernetes deployments on AWS EKS.

Software Engineer | Nexa Software Solutions (2018 - 2021)
• Developed scalable backend services in Python and Django with relational database modeling in PostgreSQL.
• Implemented automated CI/CD deployment pipelines using GitHub Actions.

EDUCATION
Master of Science in Computer Science | Stanford University (Graduated 2018)
Bachelor of Science in Information Technology | University of California, Berkeley (Graduated 2016)

PROJECTS & CERTIFICATIONS
• AWS Certified Solutions Architect - Associate
• Distributed Task Queue: Open-source Redis and Celery pipeline processing 10k tasks/sec.
"""
        },
        {
            "filename": "Elena_Rostova_DataScientist.pdf",
            "content": """Elena Rostova, Ph.D.
Email: elena.rostova@example.com | Phone: (555) 345-6789 | Location: Boston, MA
LinkedIn: linkedin.com/in/elena-rostova | GitHub: github.com/erostova

PROFESSIONAL SUMMARY
Lead Data Scientist and Machine Learning Engineer with 5+ years of experience building production predictive models, deep learning pipelines, and NLP applications. Strong mathematical foundation with Ph.D. in Computer Science.

TECHNICAL SKILLS
• AI & Machine Learning: Machine Learning, Deep Learning, NLP, Natural Language Processing, LLM, Computer Vision
• Libraries & Frameworks: PyTorch, TensorFlow, Scikit-Learn, Keras, Hugging Face, Transformers, Pandas, NumPy, SciPy
• Programming Languages: Python, R, SQL, C++
• Data Engineering: Apache Spark, Airflow, PostgreSQL, Snowflake
• Cloud & Tools: Docker, AWS, Git, Jupyter, MLflow

WORK EXPERIENCE
Staff Data Scientist | Quantum Insights Corp (2021 - Present)
• Designed end-to-end NLP screening and categorization pipelines using PyTorch and Hugging Face Transformers.
• Trained gradient-boosted trees and deep learning models achieving 94% precision on classification benchmarks.
• Deployed real-time inference models using FastAPI and Docker on AWS.

Machine Learning Researcher | BioData Analytics (2019 - 2021)
• Conducted experimental research on neural network architectures and statistical modeling using Scikit-Learn and Pandas.

EDUCATION
Ph.D. in Computer Science (Artificial Intelligence) | Massachusetts Institute of Technology (2019)
Bachelor of Science in Mathematics and Computer Science | Harvard University (2015)

CERTIFICATIONS & AWARDS
• Deep Learning Specialization Certificate
• Published 4 papers in top-tier NLP and AI conferences.
"""
        },
        {
            "filename": "Marcus_Vance_DevOps.pdf",
            "content": """Marcus Vance
Email: marcus.vance@example.com | Phone: (555) 456-7890 | Location: Seattle, WA
LinkedIn: linkedin.com/in/marcusvance | GitHub: github.com/mvance-ops

PROFESSIONAL SUMMARY
DevOps & Cloud Infrastructure Architect with 8+ years of experience managing multi-cloud platforms, Kubernetes orchestration, and immutable infrastructure-as-code.

TECHNICAL SKILLS
• Cloud Platforms: AWS, Amazon Web Services, Google Cloud, GCP, Azure
• Containerization & Orchestration: Docker, Kubernetes, Helm, Terraform, Ansible
• CI/CD & Automation: GitHub Actions, Jenkins, GitLab CI, Argo CD
• Monitoring & Observability: Prometheus, Grafana, Datadog, Sentry
• Scripting & Systems: Python, Bash, Shell, Linux, Nginx
• Security & Networking: System Design, Microservices, SSL/TLS, Zero Trust

WORK EXPERIENCE
Lead Cloud Infrastructure Engineer | CloudScale Systems (2020 - Present)
• Managed multi-region Kubernetes clusters on AWS EKS serving millions of daily active users.
• Automated 100% of infrastructure provisioning via Terraform and Ansible.
• Architected enterprise CI/CD workflows using GitHub Actions reducing deployment lead times by 65%.

Senior DevOps Engineer | DataCore Global (2016 - 2020)
• Migrated legacy monolithic applications to containerized Docker microservices.
• Established enterprise Prometheus and Grafana dashboards for cluster observability.

EDUCATION
Bachelor of Science in Computer Engineering | University of Washington (Graduated 2016)

CERTIFICATIONS
• Certified Kubernetes Administrator (CKA)
• AWS Certified Solutions Architect - Professional
"""
        },
        {
            "filename": "Chloe_Bennett_Frontend.pdf",
            "content": """Chloe Bennett
Email: chloe.bennett@example.com | Phone: (555) 567-8901 | Location: Austin, TX
LinkedIn: linkedin.com/in/chloebennett-ui | GitHub: github.com/chloeb-ui

PROFESSIONAL SUMMARY
Passionate Frontend Developer with 2+ years of experience building modern, accessible, and high-performance user interfaces. Dedicated to clean design systems and responsive web applications.

TECHNICAL SKILLS
• Frontend: React, React.js, Next.js, JavaScript, TypeScript, HTML5, CSS3, SASS
• UI Styling: Tailwind CSS, Bootstrap, Material-UI, Figma
• State & Build: Redux, Zustand, Vite, Webpack, Git
• Testing & APIs: Jest, Cypress, REST API

WORK EXPERIENCE
Junior Frontend Developer | BrightPixel Studios (2022 - Present)
• Developed component libraries and dynamic dashboards using React, Next.js, and Tailwind CSS.
• Optimized Core Web Vitals resulting in 40% faster initial page load metrics.
• Collaborated closely with product designers using Figma to implement pixel-perfect user experiences.

Frontend Engineering Intern | CreativeApps Inc (2021 - 2022)
• Built responsive landing pages and interactive forms using HTML, CSS, JavaScript, and React.

EDUCATION
Bachelor of Science in Information Technology | University of Texas at Austin (Graduated 2022)

PROJECTS
• Design System Library: Open-source collection of 30+ accessible React and Tailwind UI components.
• CryptoTracker Web App: Live cryptocurrency dashboard using React, Vite, and CoinGecko REST API.
"""
        },
        {
            "filename": "David_Kim_Backend.pdf",
            "content": """David Kim
Email: david.kim@example.com | Phone: (555) 678-9012 | Location: Chicago, IL
LinkedIn: linkedin.com/in/davidkim-backend | GitHub: github.com/dkim-code

PROFESSIONAL SUMMARY
Backend Software Engineer with 4+ years of experience building resilient APIs, microservices architectures, and asynchronous data processing pipelines with Python and relational databases.

TECHNICAL SKILLS
• Backend: Python, Django, Flask, FastAPI, REST API, Celery
• Databases & Storage: PostgreSQL, MySQL, Redis, SQLAlchemy
• Cloud & Tools: Docker, AWS, Git, Linux, Nginx, Pytest
• Core Practices: Microservices, Unit Testing, Code Review, Agile

WORK EXPERIENCE
Backend Developer | FinTech Dynamics (2021 - Present)
• Engineered secure financial transaction APIs using Python, Django, and PostgreSQL.
• Configured Redis caching layers reducing database query latencies by 50%.
• Authored comprehensive unit and integration test suites using Pytest maintaining 90%+ code coverage.

Junior Software Developer | Horizon Web Lab (2020 - 2021)
• Maintained Flask and PostgreSQL web applications and built ETL data export scripts.

EDUCATION
Bachelor of Science in Computer Science | University of Illinois Urbana-Champaign (Graduated 2020)

PROJECTS & CERTIFICATIONS
• AWS Certified Developer - Associate
• Real-time Notification Service: WebSocket and Redis Pub/Sub microservice built in FastAPI.
"""
        }
    ]

    generated_paths = []
    for s in samples:
        path = os.path.join(output_dir, s["filename"])
        create_sample_pdf(path, s["content"])
        generated_paths.append(path)
        print(f"Generated sample resume PDF: {path}")

    return generated_paths

if __name__ == "__main__":
    generate_all_samples()
