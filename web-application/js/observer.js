import { createSkillsChart } from './skillsChart.js';
import { createRolesChart } from './rolesChart.js';
import { createTransitionChart } from './transitionChart.js';

const observerOptions = {
    root: null,
    rootMargin: '0px',
    threshold: 0.3
};

const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            if (entry.target.id === 'transition-chart' && !entry.target.classList.contains('initialized')) {
                createTransitionChart();
                entry.target.classList.add('initialized');
            } else if (entry.target.id === 'skills-chart') {
                createSkillsChart();
            } else if (entry.target.id === 'roles-chart') {
                createRolesChart();
            }
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

document.addEventListener('DOMContentLoaded', () => {
    const charts = document.querySelectorAll('#transition-chart, #skills-chart, #roles-chart');
    charts.forEach(chart => observer.observe(chart));
});

let resizeTimeout;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
        const charts = document.querySelectorAll('#transition-chart.initialized, #skills-chart.initialized, #roles-chart.initialized');
        charts.forEach(chart => {
            chart.classList.remove('initialized');
            if (chart.id === 'transition-chart') {
                createTransitionChart();
            } 
            else if (chart.id === 'skills-chart') {
                createSkillsChart();
            }
            else if (chart.id === 'roles-chart') {
                createRolesChart();
            } 
        });
    }, 250);
});
