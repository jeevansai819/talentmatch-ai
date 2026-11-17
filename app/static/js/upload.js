// TalentMatch AI - Multi-Resume Drag and Drop File Uploader
document.addEventListener('DOMContentLoaded', () => {
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('file-input');
    const uploadBtn = document.getElementById('upload-btn');
    const progressContainer = document.getElementById('progress-container');
    const progressBar = document.getElementById('progress-bar');
    const progressStatus = document.getElementById('progress-status');
    const resultsContainer = document.getElementById('results-container');
    const resultsList = document.getElementById('results-list');
    const selectedFilesList = document.getElementById('selected-files-list');

    let selectedFiles = [];

    if (!dropzone || !fileInput) return;

    // Dropzone drag-over animations
    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.add('border-primary', 'bg-indigo-50');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.remove('border-primary', 'bg-indigo-50');
        }, false);
    });

    dropzone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        handleFiles(dt.files);
    });

    dropzone.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });

    function handleFiles(files) {
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            if (file.name.toLowerCase().endsWith('.pdf')) {
                // Avoid duplicates in current selection
                if (!selectedFiles.some(f => f.name === file.name && f.size === file.size)) {
                    selectedFiles.push(file);
                }
            } else {
                showToast(`Skipped '${file.name}': Only PDF files are supported.`, 'error');
            }
        }
        updateSelectedFilesUI();
    }

    function updateSelectedFilesUI() {
        if (!selectedFilesList) return;
        selectedFilesList.innerHTML = '';

        if (selectedFiles.length === 0) {
            uploadBtn.disabled = true;
            return;
        }

        uploadBtn.disabled = false;
        uploadBtn.innerHTML = `Process ${selectedFiles.length} Resume${selectedFiles.length > 1 ? 's' : ''}`;

        selectedFiles.forEach((file, idx) => {
            const item = document.createElement('div');
            item.className = 'card';
            item.style.padding = '0.75rem 1rem';
            item.style.marginBottom = '0.5rem';
            item.style.display = 'flex';
            item.style.alignItems = 'center';
            item.style.justifyContent = 'space-between';

            const sizeKb = (file.size / 1024).toFixed(1);
            item.innerHTML = `
                <div style="display:flex; align-items:center; gap:0.75rem">
                    <span style="font-size:1.2rem">📄</span>
                    <div>
                        <div style="font-weight:600; font-size:0.9rem">${file.name}</div>
                        <div style="font-size:0.75rem; color:#64748b">${sizeKb} KB</div>
                    </div>
                </div>
                <button type="button" class="btn btn-secondary btn-sm" data-idx="${idx}" style="color:#ef4444">✕</button>
            `;

            item.querySelector('button').addEventListener('click', (e) => {
                e.stopPropagation();
                selectedFiles.splice(idx, 1);
                updateSelectedFilesUI();
            });

            selectedFilesList.appendChild(item);
        });
    }

    uploadBtn.addEventListener('click', async () => {
        if (selectedFiles.length === 0) return;

        uploadBtn.disabled = true;
        uploadBtn.innerText = 'Extracting text and parsing...';
        progressContainer.style.display = 'block';
        progressBar.style.width = '30%';
        progressStatus.innerText = 'Uploading PDFs to extraction engine...';

        const formData = new FormData();
        selectedFiles.forEach(file => {
            formData.append('files', file);
        });

        try {
            progressBar.style.width = '60%';
            progressStatus.innerText = 'Parsing skills, education, and experience via NLP...';

            const res = await authFetch('/api/resumes/upload', {
                method: 'POST',
                body: formData
            });

            progressBar.style.width = '100%';
            const data = await res.json();

            if (res.ok) {
                showToast(`Processed ${data.successful_count} of ${data.total_uploaded} resumes successfully!`, 'success');
                displayUploadResults(data.results);
                selectedFiles = [];
                updateSelectedFilesUI();
                progressStatus.innerText = 'Upload and NLP extraction complete!';
            } else {
                showToast(data.detail || 'Upload failed.', 'error');
                progressStatus.innerText = 'Error occurred during processing.';
            }
        } catch (err) {
            showToast('Network error during file upload.', 'error');
            progressStatus.innerText = 'Network error.';
        } finally {
            uploadBtn.disabled = false;
            uploadBtn.innerText = 'Upload Selected Resumes';
        }
    });

    function displayUploadResults(results) {
        if (!resultsContainer || !resultsList) return;
        resultsContainer.style.display = 'block';
        resultsList.innerHTML = '';

        results.forEach(r => {
            const row = document.createElement('div');
            row.className = 'card';
            row.style.marginBottom = '0.75rem';
            row.style.padding = '1rem';
            row.style.borderLeft = r.status === 'success' ? '4px solid #10b981' : '4px solid #ef4444';

            if (r.status === 'success') {
                row.innerHTML = `
                    <div style="display:flex; justify-content:space-between; align-items:flex-start">
                        <div>
                            <div style="font-weight:700; color:#0f172a; font-size:1rem">${r.candidate_name || 'Candidate'}</div>
                            <div style="font-size:0.85rem; color:#475569; margin: 0.2rem 0">File: ${r.filename}</div>
                            <div style="display:flex; gap:0.5rem; margin-top:0.4rem">
                                <span class="badge badge-strong">${r.extracted_skills_count} Skills Detected</span>
                                <span class="badge badge-excellent">${r.experience_years.toFixed(1)} Yrs Exp</span>
                            </div>
                        </div>
                        <a href="/candidates/${r.candidate_id}" class="btn btn-outline btn-sm">View Profile →</a>
                    </div>
                `;
            } else {
                row.innerHTML = `
                    <div style="display:flex; justify-content:space-between; align-items:center">
                        <div>
                            <div style="font-weight:700; color:#ef4444">${r.filename}</div>
                            <div style="font-size:0.85rem; color:#64748b">${r.message}</div>
                        </div>
                        <span class="badge" style="background:#fef2f2; color:#991b1b">Failed</span>
                    </div>
                `;
            }
            resultsList.appendChild(row);
        });
    }
});
