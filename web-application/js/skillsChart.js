// Updated version of createSkillsChart with profession selector
export async function createSkillsChart() {
    const SKILLS_MARGIN = { top: 60, right: 90, bottom: 60, left: 200 };
    const SKILLS_TRANSITION_DURATION = 750;
    const SKILLS_BAR_HEIGHT = 35;
    const SKILLS_BAR_PADDING = 10;

    const PRIMARY_COLOR = '#7ED321';
    const TEXT_COLOR = '#2e2e2e';
    const TEXT_SECONDARY = '#6b6f76';

    try {
        const container = document.getElementById('skills-chart');
        if (container.classList.contains('initialized')) return;
        container.classList.add('initialized');
        container.innerHTML = '';

        const response = await fetch('/data/top_skills.json');
        const data = await response.json();
        const professions = data.professions;

        // Profession selector
        const selector = d3.select(container.parentNode)
            .insert('div', ':first-child')
            .attr('class', 'profession-selector')
            .style('text-align', 'center')
            .style('margin-bottom', '10px');

        selector.append('label')
            .style('color', TEXT_SECONDARY)
            .style('margin-right', '10px')
            .text('Select Profession: ');

        const professionNames = professions.map(p => p.profession_name);
        const select = selector.append('select')
            .style('padding', '5px 10px')
            .style('border-radius', '4px')
            .style('border', '1px solid #e0e0e0')
            .style('color', TEXT_COLOR)
            .style('background', 'white')
            .style('font-family', '"Courier New", Georgia')
            .on('change', function () {
                updateChart(this.value);
            });

        select.selectAll('option')
            .data(professionNames)
            .enter()
            .append('option')
            .text(d => d)
            .attr('value', d => d);

        const svg = d3.select('#skills-chart')
            .attr('width', container.clientWidth)
            .attr('height', 800);

        const g = svg.append('g')
            .attr('transform', `translate(${SKILLS_MARGIN.left},${SKILLS_MARGIN.top})`);

        const tooltip = d3.select('body').append('div')
            .attr('class', 'tooltip')
            .style('opacity', 0);

        function updateChart(professionName) {
            const selected = professions.find(p => p.profession_name === professionName);
            const skills = selected.top_skills.slice().sort((a, b) => b.number_of_professionals - a.number_of_professionals);

            const width = container.clientWidth - SKILLS_MARGIN.left - SKILLS_MARGIN.right;
            const height = (SKILLS_BAR_HEIGHT + SKILLS_BAR_PADDING) * skills.length;

            svg.attr('height', height + SKILLS_MARGIN.top + SKILLS_MARGIN.bottom);

            const xScale = d3.scaleLinear()
                .domain([0, d3.max(skills, d => d.number_of_professionals)])
                .range([0, width])
                .nice();

            const yScale = d3.scaleBand()
                .domain(skills.map(d => d.skill_name))
                .range([0, height])
                .padding(0.2);

            g.selectAll('*').remove();

            svg.select('.chart-title')?.remove();

            svg.append('text')
                .attr('class', 'chart-title')
                .attr('x', SKILLS_MARGIN.left + width / 2)
                .attr('y', SKILLS_MARGIN.top / 2)
                .attr('text-anchor', 'middle')
                .style('font-size', '16px')
                .style('font-weight', '700')
                .style('fill', TEXT_COLOR)
                .style('font-family', '"Courier New", Georgia')
                .text(`${professionName} - Top Technical Skills`);

            const bars = g.selectAll('.bar')
                .data(skills)
                .enter().append('rect')
                .attr('class', 'bar')
                .attr('y', d => yScale(d.skill_name))
                .attr('height', yScale.bandwidth())
                .attr('x', 0)
                .attr('width', d => xScale(d.number_of_professionals))
                .attr('fill', PRIMARY_COLOR)
                .attr('opacity', 0.8)
                .on('mouseover', function (event, d) {
                    d3.select(this)
                        .transition().duration(200)
                        .attr('opacity', 1);

                    tooltip.transition().duration(200).style('opacity', .9);
                    tooltip.html(`${d.number_of_professionals} professionals`)
                        .style('left', (event.pageX + 10) + 'px')
                        .style('top', (event.pageY - 28) + 'px');
                })
                .on('mouseout', function () {
                    d3.select(this).transition().duration(200).attr('opacity', 0.8);
                    tooltip.transition().duration(500).style('opacity', 0);
                });

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
                .style('font-weight', '600')
                .style('opacity', 1)
                .style('font-family', '"Courier New", Georgia')
                .text(d => d.skill_name);

            const xAxis = d3.axisBottom(xScale).ticks(5).tickFormat(d => d);
            const xAxisGroup = g.append('g')
                .attr('class', 'x-axis')
                .attr('transform', `translate(0,${height})`)
                .call(xAxis);

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
        }

        // Load chart with first profession
        updateChart(professionNames[0]);

    } catch (error) {
        console.error('Error loading skills data:', error);
    }
}