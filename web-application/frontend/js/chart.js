async function fetchData(year) {
    const response = await fetch("/employees/" + year);
    const data = await response.json();
    return data;
}

const svg = d3.select("svg");
const margin = { top: 50, right: 50, bottom: 100, left: 100 };
const width = +svg.attr("width") - margin.left - margin.right;
const height = +svg.attr("height") - margin.top - margin.bottom;
const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);
const tooltip = d3.select("#tooltip");

async function updateChart(selectedYear) {
    document.getElementById("yearLabel").innerText = selectedYear;
    
    const rawData = await fetchData(selectedYear);
    const companies = Object.keys(rawData);

    let data = [];

    for (let i = 0; i < companies.length; i++) {
        company = companies[i];
        for (let j = 0; j < rawData[company].length; j++) {
            let row = rawData[company][j];
            row.j = j;
            data.push(row)
        }
    }

    const bubbleSize = 30;
    const rowSpacing = 4;
    const rowsNeeded = Math.ceil(data.length / companies.length);
    const newHeight = rowsNeeded * (bubbleSize + rowSpacing) + 100;

    d3.select("svg").attr("height", newHeight);
    const height = newHeight - margin.top - margin.bottom;

    const x = d3.scaleBand().domain(companies).range([0, width]).padding(0.5);
    const colorScale = d3.scaleOrdinal().domain(companies).range(d3.schemeCategory10);

    g.selectAll(".x-axis").remove();
    g.append("g")
        .attr("class", "x-axis")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(x));

    const bubbles = g.selectAll(".bubble").data(data);

    bubbles.enter()
        .append("circle")
        .attr("class", "bubble")
        .attr("r", 2)
        .merge(bubbles)
        .transition().duration(500)
        .attr("cx", d => x(d.company) + x.bandwidth() / 2)
        .attr("cy", (d, i) => height - (d.j * 4) - 50)
        .attr("fill", d => colorScale(d.company));

    bubbles.exit().remove();
    
    g.selectAll(".bubble")
        .on("mouseover", function(event, d) {
            tooltip.style("display", "block")
                   .html(`User: ${d.name}<br>Company: ${d.company}<br>Start: ${d.start_year}<br>End: ${d.end_year}`)
                   .style("left", (event.pageX + 10) + "px")
                   .style("top", (event.pageY - 20) + "px");
        })
        .on("mousemove", function(event) {
            tooltip.style("left", (event.pageX + 10) + "px")
                   .style("top", (event.pageY - 20) + "px");
        })
        .on("mouseout", function() {
            tooltip.style("display", "none");
        });
}

(async function initialize() {
    await updateChart(2019);
    document.getElementById("yearSlider").addEventListener("input", function () {
        updateChart(this.value);
    });
})();