// Constants for the skills chart
const SKILLS_MARGIN = { top: 60, right: 90, bottom: 60, left: 200 }; // Увеличили left и right margin
const SKILLS_TRANSITION_DURATION = 750;
const SKILLS_BAR_HEIGHT = 35;
const SKILLS_BAR_PADDING = 10;

// Colors from CSS variables
const PRIMARY_COLOR = '#7ED321';
const TEXT_COLOR = '#2e2e2e';
const TEXT_SECONDARY = '#6b6f76';
const BACKGROUND_COLOR = '#edf0f4';

// Create intersection observer for animations
const observerOptions = {
    root: null,
    rootMargin: '0px',
    threshold: 0.3 // Trigger when 30% of the element is visible
};

const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            // If this is a chart container, create the chart
            if (entry.target.id === 'skills-chart') {
                createSkillsChart();
            }
            // You can add more chart types here
            
            // Unobserve after creating the chart
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// Observe all chart containers
document.addEventListener('DOMContentLoaded', () => {
    const charts = document.querySelectorAll('#skills-chart, #roles-chart'); // Add all chart containers here
    charts.forEach(chart => observer.observe(chart));
});

// Create and render the skills chart
async function createSkillsChart() {
    try {
        // Get the container and check if it's already initialized
        const container = document.getElementById('skills-chart');
        if (container.classList.contains('initialized')) return;
        
        // Mark as initialized
        container.classList.add('initialized');
        
        // Clear any existing content
        container.innerHTML = '';
        
        // Fetch the skills data
        const response = await fetch('/data/top_skills.json');
        const data = await response.json();
        const skills = data.top_skills;

        // Sort skills by number of professionals
        skills.sort((a, b) => b.number_of_professionals - a.number_of_professionals);

        // Setup the chart dimensions
        const width = container.clientWidth - SKILLS_MARGIN.left - SKILLS_MARGIN.right;
        const height = (SKILLS_BAR_HEIGHT + SKILLS_BAR_PADDING) * skills.length;

        // Create scales
        const xScale = d3.scaleLinear()
            .domain([0, d3.max(skills, d => d.number_of_professionals)])
            .range([0, width])
            .nice();

        const yScale = d3.scaleBand()
            .domain(skills.map(d => d.skill_name))
            .range([0, height])
            .padding(0.2);

        // Create SVG
        const svg = d3.select('#skills-chart')
            .attr('width', width + SKILLS_MARGIN.left + SKILLS_MARGIN.right)
            .attr('height', height + SKILLS_MARGIN.top + SKILLS_MARGIN.bottom);

        // Add title to the chart
        svg.append('text')
            .attr('class', 'chart-title')
            .attr('x', SKILLS_MARGIN.left + width / 2)
            .attr('y', SKILLS_MARGIN.top / 2)
            .attr('text-anchor', 'middle')
            .style('font-size', '16px')
            .style('font-weight', '600')
            .style('fill', TEXT_COLOR)
            .text('Top Technical Skills Distribution');

        const g = svg.append('g')
            .attr('transform', `translate(${SKILLS_MARGIN.left},${SKILLS_MARGIN.top})`);

        // Create tooltip with only number of professionals
        const tooltip = d3.select('body').append('div')
            .attr('class', 'tooltip')
            .style('opacity', 0);

        // Add bars with initial width of 0
        const bars = g.selectAll('.bar')
            .data(skills)
            .enter().append('rect')
            .attr('class', 'bar')
            .attr('y', d => yScale(d.skill_name))
            .attr('height', yScale.bandwidth())
            .attr('x', 0)
            .attr('width', 0) // Start with width 0
            .attr('fill', PRIMARY_COLOR)
            .attr('opacity', 0.8)
            .on('mouseover', function(event, d) {
                d3.select(this)
                    .transition()
                    .duration(200)
                    .attr('opacity', 1);

                tooltip.transition()
                    .duration(200)
                    .style('opacity', .9);
                tooltip.html(`${d.number_of_professionals} professionals`)
                    .style('left', (event.pageX + 10) + 'px')
                    .style('top', (event.pageY - 28) + 'px');
            })
            .on('mouseout', function() {
                d3.select(this)
                    .transition()
                    .duration(200)
                    .attr('opacity', 0.8);

                tooltip.transition()
                    .duration(500)
                    .style('opacity', 0);
            });

        // Add labels with initial opacity 0
        const labels = g.selectAll('.label')
            .data(skills)
            .enter().append('text')
            .attr('class', 'label')
            .attr('y', d => yScale(d.skill_name) + yScale.bandwidth() / 2)
            .attr('x', -10)
            .attr('text-anchor', 'end')
            .attr('dominant-baseline', 'middle')
            .attr('fill', TEXT_COLOR)
            .style('font-size', '14px')
            .style('font-weight', '500')
            .style('opacity', 0)
            .text(d => d.skill_name);

        // Add x-axis with initial opacity 0
        const xAxis = d3.axisBottom(xScale)
            .ticks(5)
            .tickFormat(d => d);

        const xAxisGroup = g.append('g')
            .attr('class', 'x-axis')
            .attr('transform', `translate(0,${height})`)
            .style('opacity', 0)
            .call(xAxis);

        // Style gridlines
        xAxisGroup.selectAll('.tick line')
            .attr('stroke', 'rgba(0,0,0,0.1)')
            .attr('stroke-dasharray', '2,2');

        // Style axis path
        xAxisGroup.select('.domain')
            .attr('stroke', TEXT_SECONDARY)
            .attr('stroke-opacity', 0.2);

        // Add axis labels
        g.append('text')
            .attr('class', 'x-axis-label')
            .attr('x', width / 2)
            .attr('y', height + 45)
            .attr('text-anchor', 'middle')
            .style('fill', TEXT_SECONDARY)
            .style('font-size', '14px')
            .text('Number of Professionals');

        g.append('text')
            .attr('class', 'y-axis-label')
            .attr('transform', 'rotate(-90)')
            .attr('x', -height / 2)
            .attr('y', -SKILLS_MARGIN.left + 50)
            .attr('text-anchor', 'middle')
            .style('fill', TEXT_SECONDARY)
            .style('font-size', '14px')
            .text('Technical Skills');

        // Animate everything in sequence
        // 1. Fade in labels
        labels.transition()
            .duration(500)
            .style('opacity', 1);

        // 2. Animate bars
        bars.transition()
            .delay(500)
            .duration(SKILLS_TRANSITION_DURATION)
            .attr('width', d => xScale(d.number_of_professionals));

        // 3. Fade in x-axis
        xAxisGroup.transition()
            .delay(500 + SKILLS_TRANSITION_DURATION * 0.5)
            .duration(500)
            .style('opacity', 1);

    } catch (error) {
        console.error('Error loading skills data:', error);
    }
}

// Handle window resize
let resizeTimeout;
window.addEventListener('resize', () => {
    // Debounce resize event
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
        const charts = document.querySelectorAll('#skills-chart.initialized, #roles-chart.initialized');
        charts.forEach(chart => {
            chart.classList.remove('initialized');
            if (chart.id === 'skills-chart') {
                createSkillsChart();
            }
            // Add other chart recreate functions here
        });
    }, 250);
});