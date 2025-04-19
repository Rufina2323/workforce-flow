export async function createRolesChart() {
    const ROLES_MARGIN = { top: 30, right: 40, bottom: 40, left: 40 };
    const ROLES_TRANSITION_DURATION = 750;
    const PIE_RADIUS = 120;

    const PRIMARY_COLOR = '#7ED321';
    const TEXT_COLOR = '#2e2e2e';
    const TEXT_SECONDARY = '#6b6f76';

    try {
        const container = document.getElementById('roles-chart');
        if (container.classList.contains('initialized')) return;

        container.classList.add('initialized');
        container.innerHTML = '';

        const response = await fetch('/data/professions.json');
        const data = await response.json();

        const currentYear = "2025";
        const currentYearData = Object.entries(data[currentYear]).map(([profession_name, number_of_professionals]) => ({
            profession_name,
            number_of_professionals
        }));

        const width = container.clientWidth - ROLES_MARGIN.left - ROLES_MARGIN.right;
        const height = 420;

        const svg = d3.select('#roles-chart')
            .attr('width', width + ROLES_MARGIN.left + ROLES_MARGIN.right)
            .attr('height', height + ROLES_MARGIN.top + ROLES_MARGIN.bottom)
            .append('g')
            .attr('transform', `translate(${ROLES_MARGIN.left},${ROLES_MARGIN.top})`);

        svg.append('text')
            .attr('class', 'chart-title')
            .attr('x', width / 2)
            .attr('y', 5)
            .attr('text-anchor', 'middle')
            .style('font-size', '16px')
            .style('font-weight', '700')
            .style('fill', TEXT_COLOR)
            .style('font-family', '"Courier New", Georgia')
            .text('Job Roles Distribution');

        const years = Object.keys(data).sort();
        const yearSelector = d3.select(container.parentNode)
            .insert('div', ':first-child')
            .attr('class', 'year-selector')
            .style('text-align', 'center')
            .style('margin-bottom', '10px');

        yearSelector.append('label')
            .style('color', TEXT_SECONDARY)
            .style('margin-right', '10px')
            .text('Select Year: ');

        yearSelector.append('select')
            .style('padding', '5px 10px')
            .style('border-radius', '4px')
            .style('border', '1px solid #e0e0e0')
            .style('color', TEXT_COLOR)
            .style('background', 'white')
            .on('change', function() {
                updateChart(this.value);
            })
            .selectAll('option')
            .data(years)
            .enter()
            .append('option')
            .text(d => d)
            .attr('value', d => d)
            .property('selected', d => d === currentYear);

        const pieGroup = svg.append('g')
            .attr('transform', `translate(${width / 2}, ${(height / 2) - 30})`);

        const colorScale = d3.scaleOrdinal()
            .domain(Object.keys(currentYearData.map(d => d.profession_name)))
            .range([
                '#FFB37F', '#88E27B', '#FFF27A', '#81C7F5', '#9C97F7',
                '#F48484', '#C6C6C6', '#F9A1D0', '#7ED0E7', '#94E7B6'
            ]);

        const pie = d3.pie()
            .value(d => d.number_of_professionals)
            .sort(null);

        const arc = d3.arc()
            .innerRadius(PIE_RADIUS * 0.5)
            .outerRadius(PIE_RADIUS);

        const tooltip = d3.select('body').append('div')
            .attr('class', 'tooltip')
            .style('opacity', 0);

        function updateChart(year) {
            const yearDataRaw = data[year];
            const yearData = Object.entries(yearDataRaw).map(([profession_name, number_of_professionals]) => ({
                profession_name,
                number_of_professionals
            }));

            const paths = pieGroup.selectAll('path')
                .data(pie(yearData));

            paths.exit().remove();

            paths.transition()
                .duration(ROLES_TRANSITION_DURATION)
                .attrTween('d', function(d) {
                    const interpolate = d3.interpolate(this._current || d, d);
                    this._current = interpolate(0);
                    return t => arc(interpolate(t));
                });

            paths.enter()
                .append('path')
                .each(function(d) { this._current = d; })
                .attr('fill', d => colorScale(d.data.profession_name))
                .attr('stroke', 'white')
                .attr('stroke-width', 1)
                .style('opacity', 0.85)
                .attr('d', arc)
                .style('cursor', 'pointer')
                .on('mouseover', function(event, d) {
                    d3.select(this)
                        .transition()
                        .duration(200)
                        .attr('transform', function() {
                            const centroid = arc.centroid(d);
                            return `translate(${centroid[0] * 0.05},${centroid[1] * 0.05})`;
                        });

                    tooltip.transition()
                        .duration(200)
                        .style('opacity', 0.9);

                    const percentage = ((d.data.number_of_professionals /
                        yearData.reduce((acc, curr) => acc + curr.number_of_professionals, 0)) * 100).toFixed(1);

                    tooltip.html(`
                        <strong>${d.data.profession_name}</strong><br/>
                        Professionals: ${d.data.number_of_professionals}<br/>
                        Share: ${percentage}%
                    `)
                    .style('left', (event.pageX + 10) + 'px')
                    .style('top', (event.pageY - 28) + 'px');
                })
                .on('mouseout', function() {
                    d3.select(this)
                        .transition()
                        .duration(200)
                        .attr('transform', 'translate(0,0)');

                    tooltip.transition()
                        .duration(500)
                        .style('opacity', 0);
                });

            const centerText = pieGroup.selectAll('.center-text')
                .data([year]);

            centerText.enter()
                .append('text')
                .attr('class', 'center-text')
                .merge(centerText)
                .attr('text-anchor', 'middle')
                .attr('dy', '0.35em')
                .style('font-size', '24px')
                .style('font-weight', '600')
                .style('fill', TEXT_COLOR)
                .style('font-family', '"Roboto Mono", monospace')
                .text(year);

            svg.selectAll('.legend').remove();

            const legendRectSize = 12;
            const legendY = height - 60;
            const itemsPerColumn = 5;
            const columnWidth = width / 2;
            const itemHeight = 20;

            const legend = svg.append('g')
                .attr('class', 'legend-container')
                .attr('transform', `translate(0, ${legendY})`);

            const legendItems = legend.selectAll('.legend')
                .data(yearData)
                .enter()
                .append('g')
                .attr('class', 'legend')
                .attr('transform', function(d, i) {
                    const column = Math.floor(i / itemsPerColumn);
                    const row = i % itemsPerColumn;
                    const x = column * columnWidth + (columnWidth - 180) / 2;
                    const y = row * itemHeight;
                    return `translate(${x}, ${y})`;
                });

            legendItems.append('rect')
                .attr('width', legendRectSize)
                .attr('height', legendRectSize)
                .attr('rx', 2)
                .attr('x', 0)
                .attr('y', 0)
                .style('fill', d => colorScale(d.profession_name))
                .style('opacity', 0.85);

            legendItems.append('text')
                .attr('x', legendRectSize + 8)
                .attr('y', 11)
                .text(d => d.profession_name)
                .style('font-family', '"Roboto Mono", monospace')
                .style('font-size', '12px')
                .style('font-weight', '600')
                .style('fill', TEXT_SECONDARY);

            legendItems.on('mouseover', function(event, d) {
                const segment = pieGroup.selectAll('path')
                    .filter(p => p.data.profession_name === d.profession_name);

                segment.transition()
                    .duration(200)
                    .attr('transform', function(p) {
                        const centroid = arc.centroid(p);
                        return `translate(${centroid[0] * 0.05},${centroid[1] * 0.05})`;
                    });

                const percentage = ((d.number_of_professionals /
                    yearData.reduce((acc, curr) => acc + curr.number_of_professionals, 0)) * 100).toFixed(1);

                tooltip.transition()
                    .duration(200)
                    .style('opacity', 0.9);

                tooltip.html(`
                    <strong>${d.profession_name}</strong><br/>
                    Professionals: ${d.number_of_professionals}<br/>
                    Share: ${percentage}%
                `)
                .style('left', (event.pageX + 10) + 'px')
                .style('top', (event.pageY - 28) + 'px');
            }).on('mouseout', function(event, d) {
                pieGroup.selectAll('path')
                    .filter(p => p.data.profession_name === d.profession_name)
                    .transition()
                    .duration(200)
                    .attr('transform', 'translate(0,0)');

                tooltip.transition()
                    .duration(500)
                    .style('opacity', 0);
            });
        }

        updateChart(currentYear);

    } catch (error) {
        console.error('Error loading roles data:', error);
    }
}
