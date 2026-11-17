"""
Application constants, taxonomies, and hierarchies.
"""

APPLICATION_STATUSES = [
    "New",
    "Under Review",
    "Shortlisted",
    "Interview Scheduled",
    "Rejected",
    "Hired"
]

EMPLOYMENT_TYPES = [
    "Full-time",
    "Part-time",
    "Contract",
    "Internship",
    "Remote"
]

SCORE_TIERS = {
    "EXCELLENT": {"min": 90.0, "label": "Excellent Match", "badge": "bg-emerald-100 text-emerald-800 border-emerald-200"},
    "STRONG": {"min": 75.0, "label": "Strong Match", "badge": "bg-indigo-100 text-indigo-800 border-indigo-200"},
    "MODERATE": {"min": 60.0, "label": "Moderate Match", "badge": "bg-amber-100 text-amber-800 border-amber-200"},
    "LOW": {"min": 0.0, "label": "Low Match", "badge": "bg-slate-100 text-slate-700 border-slate-200"}
}

# Educational Degree Hierarchy (Normalized Score 1 to 5)
DEGREE_HIERARCHY = {
    "doctorate": 5,
    "phd": 5,
    "master": 4,
    "msc": 4,
    "ms": 4,
    "mtech": 4,
    "mba": 4,
    "mca": 4,
    "bachelor": 3,
    "bsc": 3,
    "bs": 3,
    "btech": 3,
    "be": 3,
    "bca": 3,
    "bba": 3,
    "associate": 2,
    "diploma": 2,
    "high school": 1,
    "secondary": 1
}

# Comprehensive Technical Skill Taxonomy
TECHNICAL_SKILLS_TAXONOMY = {
    "Programming Languages": [
        "python", "javascript", "typescript", "java", "c++", "c#", "c", "go", "golang",
        "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "dart", "perl",
        "shell", "bash", "powershell", "matlab", "solidity", "lua", "haskell", "clojure"
    ],
    "Web & Frontend Frameworks": [
        "react", "react.js", "next.js", "nextjs", "vue", "vue.js", "nuxt.js", "angular",
        "svelte", "sveltekit", "html", "html5", "css", "css3", "sass", "scss",
        "tailwind", "tailwindcss", "bootstrap", "material-ui", "mui", "redux", "zustand",
        "webpack", "vite", "jquery", "graphql", "rest api", "websocket", "remix"
    ],
    "Backend Frameworks": [
        "fastapi", "flask", "django", "express", "express.js", "nest.js", "nestjs",
        "node.js", "nodejs", "spring", "spring boot", "ruby on rails", "rails",
        ".net", ".net core", "asp.net", "laravel", "gin", "fiber", "actix-web",
        "grpc", "celery", "tornado", "aiohttp", "koa"
    ],
    "Databases & Caching": [
        "postgresql", "postgres", "mysql", "sqlite", "mongodb", "redis", "elasticsearch",
        "cassandra", "dynamodb", "oracle", "sql server", "mariadb", "neo4j", "couchdb",
        "snowflake", "bigquery", "redshift", "clickhouse", "pinecone", "milvus", "weaviate",
        "supabase", "firebase", "firestore", "prisma", "sqlalchemy", "hibernate"
    ],
    "Cloud & Infrastructure": [
        "aws", "amazon web services", "azure", "google cloud", "gcp", "docker", "kubernetes",
        "k8s", "terraform", "ansible", "helm", "serverless", "lambda", "cloud run",
        "ec2", "s3", "ecs", "eks", "cloudflare", "nginx", "apache", "traefik", "linux"
    ],
    "DevOps & CI/CD": [
        "git", "github", "gitlab", "bitbucket", "jenkins", "github actions", "gitlab ci",
        "circleci", "argo cd", "prometheus", "grafana", "datadog", "new relic", "splunk",
        "sentry", "sonarqube", "jira", "confluence"
    ],
    "AI, ML & Data Science": [
        "machine learning", "deep learning", "nlp", "natural language processing",
        "computer vision", "llm", "large language models", "generative ai", "tensorflow",
        "pytorch", "scikit-learn", "keras", "spacy", "nltk", "hugging face", "transformers",
        "langchain", "llamaindex", "opencv", "pandas", "numpy", "scipy", "matplotlib",
        "seaborn", "tableau", "power bi", "apache spark", "hadoop", "airflow", "kafka"
    ],
    "Testing & Quality Assurance": [
        "pytest", "unittest", "jest", "mocha", "cypress", "playwright", "selenium",
        "postman", "swagger", "junit", "test automation", "load testing", "locust"
    ],
    "Methodologies & Soft Skills": [
        "agile", "scrum", "kanban", "ci/cd", "microservices", "system design",
        "code review", "tdd", "test driven development", "clean architecture",
        "mentorship", "leadership", "communication", "problem solving"
    ]
}

# Custom canonical brand casing overrides
BRAND_CASING = {
    "fastapi": "FastAPI",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "mongodb": "MongoDB",
    "mysql": "MySQL",
    "sqlite": "SQLite",
    "graphql": "GraphQL",
    "next.js": "Next.js",
    "nextjs": "Next.js",
    "react.js": "React",
    "react": "React",
    "vue.js": "Vue.js",
    "vue": "Vue.js",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "pytorch": "PyTorch",
    "scikit-learn": "Scikit-Learn",
    "tensorflow": "TensorFlow",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "terraform": "Terraform",
    "aws": "AWS",
    "gcp": "GCP",
    "ci/cd": "CI/CD",
    "github": "GitHub",
    "gitlab": "GitLab",
    "rest api": "REST API"
}

# Inverted dictionary for fast O(1) canonical skill lookup
CANONICAL_SKILL_MAP = {}
for category, skills in TECHNICAL_SKILLS_TAXONOMY.items():
    for skill in skills:
        key = skill.lower()
        if key in BRAND_CASING:
            canon = BRAND_CASING[key]
        elif len(skill) <= 3:
            canon = skill.upper()
        elif skill.endswith("js"):
            canon = skill[:-2].title() + ".js"
        else:
            canon = skill.title()
        CANONICAL_SKILL_MAP[key] = {
            "canonical": canon,
            "category": category
        }
