import { createSkillsChart } from './skillsChart.js';
import { createRolesChart } from './rolesChart.js';

const observerOptions = {
    root: null,
    rootMargin: '0px',
    threshold: 0.3
};

const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            if (entry.target.id === 'skills-chart') {
                createSkillsChart();
            } else if (entry.target.id === 'roles-chart') {
                createRolesChart();
            }
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

document.addEventListener('DOMContentLoaded', () => {
    const charts = document.querySelectorAll('#skills-chart, #roles-chart');
    charts.forEach(chart => observer.observe(chart));
});

let resizeTimeout;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
        const charts = document.querySelectorAll('#skills-chart.initialized, #roles-chart.initialized');
        charts.forEach(chart => {
            chart.classList.remove('initialized');
            if (chart.id === 'skills-chart') {
                createSkillsChart();
            } else if (chart.id === 'roles-chart') {
                createRolesChart();
            }
        });
    }, 250);
});
