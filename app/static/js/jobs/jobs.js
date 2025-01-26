let page = 1;
let loading = false;
let hasMore = true;
const jobsContainer = document.querySelector('.row');

// Remove fixed height
document.querySelector("body").style.height = 'auto';

window.addEventListener("scroll", debounce(function() {
    if (loading || !hasMore) return;

    const {scrollTop, scrollHeight, clientHeight} = document.documentElement;
    
    if (scrollTop + clientHeight >= scrollHeight - 5) {
        loadMoreJobs();
    }
}, 200));

async function loadMoreJobs() {
    loading = true;
    showLoader();
    
    try {
        const response = await fetch(`/jobs/api/load?page=${page}`);
        const data = await response.json();
        
        if (data.jobs.length === 0) {
            hasMore = false;
            hideLoader();
            return;
        }

        renderJobs(data.jobs);
        page++;
        
    } catch (error) {
        console.error('Error loading jobs:', error);
    } finally {
        loading = false;
        hideLoader();
    }
}

function showLoader() {
    if (!document.querySelector('.loader')) {
        const loader = document.createElement('div');
        loader.className = 'loader text-center my-3';
        loader.innerHTML = '<div class="spinner-border" role="status"></div>';
        jobsContainer.parentNode.insertBefore(loader, jobsContainer.nextSibling);
    }
}

function hideLoader() {
    const loader = document.querySelector('.loader');
    if (loader) loader.remove();
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function renderJobs(jobs) {
    const template = jobs.map(job => `
        <div class="col">
            <div class="card h-100 shadow-sm">
                <div class="card-body">
                    <h5 class="card-title text-primary">${job.title}</h5>
                    <h6 class="card-subtitle mb-2 text-muted">
                        <i class="fas fa-building me-2"></i>${job.company.name}
                    </h6>
                    <p class="card-text">
                        <i class="fas fa-map-marker-alt me-2"></i>${job.location}<br>
                        <i class="fas fa-dollar-sign me-2"></i>${job.salary}
                    </p>
                    <p class="card-text text-muted small">
                        ${job.description.substring(0, 150)}...
                    </p>
                </div>
            </div>
        </div>
    `).join('');
    
    jobsContainer.insertAdjacentHTML('beforeend', template);
}