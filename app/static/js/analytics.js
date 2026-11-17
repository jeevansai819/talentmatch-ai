// TalentMatch AI - Live Analytics & Chart.js Visualizations
document.addEventListener('DOMContentLoaded', async () => {
    const kpiResumes = document.getElementById('kpi-resumes');
    const kpiJobs = document.getElementById('kpi-jobs');
    const kpiCandidates = document.getElementById('kpi-candidates');
    const kpiShortlisted = document.getElementById('kpi-shortlisted');
    const kpiAvgScore = document.getElementById('kpi-avg-score');

    try {
        const res = await authFetch('/api/analytics/dashboard');
        if (!res.ok) return;
        const data = await res.json();

        // Update KPIs
        if (kpiResumes) kpiResumes.innerText = data.total_resumes;
        if (kpiJobs) kpiJobs.innerText = data.total_active_jobs;
        if (kpiCandidates) kpiCandidates.innerText = data.total_candidates;
        if (kpiShortlisted) kpiShortlisted.innerText = data.total_shortlisted;
        if (kpiAvgScore) kpiAvgScore.innerText = `${data.average_matching_score}%`;

        // 1. Common Skills Bar Chart
        const skillsCtx = document.getElementById('skillsChart');
        if (skillsCtx && window.Chart) {
            new Chart(skillsCtx, {
                type: 'bar',
                data: {
                    labels: data.skills_distribution.map(s => s.skill),
                    datasets: [{
                        label: 'Candidate Count',
                        data: data.skills_distribution.map(s => s.count),
                        backgroundColor: '#4f46e5',
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { beginAtZero: true, ticks: { precision: 0 } },
                        x: { grid: { display: false } }
                    }
                }
            });
        }

        // 2. Experience Distribution Doughnut Chart
        const expCtx = document.getElementById('experienceChart');
        if (expCtx && window.Chart) {
            new Chart(expCtx, {
                type: 'doughnut',
                data: {
                    labels: data.experience_distribution.map(e => e.label),
                    datasets: [{
                        data: data.experience_distribution.map(e => e.count),
                        backgroundColor: ['#6366f1', '#06b6d4', '#10b981', '#f59e0b']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { position: 'bottom' } }
                }
            });
        }

        // 3. Match Score Distribution Chart
        const scoreCtx = document.getElementById('scoreChart');
        if (scoreCtx && window.Chart) {
            new Chart(scoreCtx, {
                type: 'bar',
                data: {
                    labels: data.match_score_distribution.map(m => m.label),
                    datasets: [{
                        label: 'Candidates in Score Bracket',
                        data: data.match_score_distribution.map(m => m.count),
                        backgroundColor: ['#10b981', '#6366f1', '#f59e0b', '#94a3b8'],
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { beginAtZero: true, ticks: { precision: 0 } },
                        x: { grid: { display: false } }
                    }
                }
            });
        }

        // 4. Candidate Recruitment Status Breakdown
        const statusCtx = document.getElementById('statusChart');
        if (statusCtx && window.Chart) {
            new Chart(statusCtx, {
                type: 'doughnut',
                data: {
                    labels: data.status_distribution.map(s => s.label),
                    datasets: [{
                        data: data.status_distribution.map(s => s.count),
                        backgroundColor: ['#94a3b8', '#38bdf8', '#818cf8', '#a855f7', '#f43f5e', '#10b981']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { position: 'bottom' } }
                }
            });
        }

    } catch (err) {
        console.error('Failed to load dashboard analytics:', err);
    }
});
