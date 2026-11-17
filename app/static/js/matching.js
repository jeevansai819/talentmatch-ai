// TalentMatch AI - Candidate Ranking, Screening & Comparison Engine
document.addEventListener('DOMContentLoaded', () => {
    const runMatchBtn = document.getElementById('run-match-btn');
    const jobSelector = document.getElementById('job-selector');
    const tierFilter = document.getElementById('tier-filter');
    const sortFilter = document.getElementById('sort-filter');
    const minExpFilter = document.getElementById('min-exp-filter');
    const compareBtn = document.getElementById('compare-btn');

    if (runMatchBtn) {
        runMatchBtn.addEventListener('click', async () => {
            const jobId = runMatchBtn.dataset.jobId || (jobSelector ? jobSelector.value : null);
            if (!jobId) {
                showToast('Please select a job description first.', 'error');
                return;
            }

            runMatchBtn.disabled = true;
            runMatchBtn.innerHTML = '⚙ Processing NLP & Match Scores...';

            try {
                const res = await authFetch(`/api/matching/${jobId}/run`, {
                    method: 'POST',
                    body: JSON.stringify({})
                });
                const data = await res.json();
                if (res.ok) {
                    showToast(data.message, 'success');
                    setTimeout(() => window.location.reload(), 600);
                } else {
                    showToast(data.detail || 'Matching calculation failed.', 'error');
                }
            } catch (err) {
                showToast('Failed to trigger matching engine.', 'error');
            } finally {
                runMatchBtn.disabled = false;
                runMatchBtn.innerHTML = '⚡ Run Matching Engine';
            }
        });
    }

    // Auto-reload on job selector change
    if (jobSelector) {
        jobSelector.addEventListener('change', () => {
            const jobId = jobSelector.value;
            window.location.href = `/ranking?job_id=${jobId}`;
        });
    }

    // Filter changes
    function applyFilters() {
        const rows = document.querySelectorAll('.candidate-rank-row');
        const selectedTier = tierFilter ? tierFilter.value.toLowerCase() : '';
        const minExp = minExpFilter ? parseFloat(minExpFilter.value) || 0 : 0;

        rows.forEach(row => {
            const rowTier = (row.dataset.tier || '').toLowerCase();
            const rowExp = parseFloat(row.dataset.exp) || 0;

            let matchesTier = !selectedTier || rowTier.includes(selectedTier);
            let matchesExp = rowExp >= minExp;

            if (matchesTier && matchesExp) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }

    if (tierFilter) tierFilter.addEventListener('change', applyFilters);
    if (minExpFilter) minExpFilter.addEventListener('input', applyFilters);

    // Candidate Comparison
    if (compareBtn) {
        compareBtn.addEventListener('click', async () => {
            const checkedBoxes = document.querySelectorAll('.compare-checkbox:checked');
            if (checkedBoxes.length < 2) {
                showToast('Select at least 2 candidates (up to 5) to compare side-by-side.', 'info');
                return;
            }
            if (checkedBoxes.length > 5) {
                showToast('You can compare a maximum of 5 candidates at once.', 'error');
                return;
            }

            const candidateIds = Array.from(checkedBoxes).map(cb => parseInt(cb.value));
            const jobId = runMatchBtn ? runMatchBtn.dataset.jobId : (jobSelector ? jobSelector.value : null);

            try {
                const res = await authFetch('/api/matching/compare', {
                    method: 'POST',
                    body: JSON.stringify({ job_id: parseInt(jobId), candidate_ids: candidateIds })
                });
                const data = await res.json();
                if (res.ok) {
                    renderComparisonModal(data);
                } else {
                    showToast(data.detail || 'Failed to compare candidates.', 'error');
                }
            } catch (err) {
                showToast('Error during candidate comparison.', 'error');
            }
        });
    }

    function renderComparisonModal(data) {
        const body = document.getElementById('comparison-modal-body');
        if (!body) return;

        let colsHtml = '';
        data.candidates.forEach(c => {
            const tierColor = c.overall_score >= 90 ? '#10b981' : c.overall_score >= 75 ? '#6366f1' : c.overall_score >= 60 ? '#f59e0b' : '#64748b';
            colsHtml += `
                <div style="flex:1; min-width:240px; border:1px solid #e2e8f0; border-radius:12px; padding:1.25rem; background:#fff">
                    <div style="font-weight:700; font-size:1.1rem; color:#0f172a; margin-bottom:0.25rem">${c.name}</div>
                    <div style="font-size:1.5rem; font-weight:800; color:${tierColor}">${c.overall_score}%</div>
                    <span class="badge" style="margin-bottom:1rem">${c.match_tier}</span>
                    
                    <div style="margin-top:0.75rem; font-size:0.85rem">
                        <div style="margin-bottom:0.4rem"><b>Experience:</b> ${c.experience_years.toFixed(1)} yrs</div>
                        <div style="margin-bottom:0.4rem"><b>Education:</b> ${c.education}</div>
                        <div style="margin-bottom:0.4rem"><b>Status:</b> ${c.current_status}</div>
                    </div>

                    <div style="margin-top:1rem; border-top:1px solid #f1f5f9; padding-top:0.75rem">
                        <div style="font-size:0.8rem; font-weight:700; color:#475569; text-transform:uppercase; margin-bottom:0.35rem">Matched Skills</div>
                        <div style="display:flex; flex-wrap:wrap; gap:0.25rem">
                            ${c.matched_required_skills.slice(0, 5).map(s => `<span class="skill-chip" style="background:#ecfdf5; color:#065f46">${s}</span>`).join('')}
                        </div>
                    </div>

                    <div style="margin-top:0.75rem; border-top:1px solid #f1f5f9; padding-top:0.75rem">
                        <div style="font-size:0.8rem; font-weight:700; color:#475569; text-transform:uppercase; margin-bottom:0.35rem">Key Strengths</div>
                        <ul style="font-size:0.8rem; color:#334155; padding-left:1rem">
                            ${c.strengths.slice(0, 2).map(s => `<li>${s}</li>`).join('')}
                        </ul>
                    </div>

                    <div style="margin-top:1.25rem">
                        <a href="/candidates/${c.candidate_id}" class="btn btn-primary btn-sm" style="width:100%">Full Profile →</a>
                    </div>
                </div>
            `;
        });

        body.innerHTML = `
            <div style="margin-bottom:1rem; color:#64748b; font-size:0.9rem">Comparing candidates for role: <b>${data.job_title}</b></div>
            <div style="display:flex; gap:1rem; overflow-x:auto; padding-bottom:0.5rem">
                ${colsHtml}
            </div>
        `;

        openModal('comparison-modal');
    }
});
