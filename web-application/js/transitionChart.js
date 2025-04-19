export async function createTransitionChart() {
  const container = document.getElementById("transition-chart");
  if (!container) return;

  const width = container.clientWidth;
  const height = 600;
  container.innerHTML = "";

  // Add controls container with fixed width and centered
  const controlsContainer = d3.select(container)
    .append("div")
    .attr("class", "time-controls")
    .style("display", "flex")
    .style("align-items", "center")
    .style("justify-content", "center")
    .style("gap", "10px")
    .style("margin-bottom", "20px");

  // Add time display container
  const timeDisplayContainer = controlsContainer
    .append("div")
    .attr("class", "time-display-container")
    .style("display", "flex")
    .style("align-items", "center")
    .style("gap", "10px")
    .style("padding", "8px")
    .style("background", "rgba(255, 255, 255, 0.9)")
    .style("border-radius", "4px")
    .style("box-shadow", "0 1px 3px rgba(0,0,0,0.1)")
    .style("width", "240px"); // Increased width to accommodate reset button

  // Add year and month on the same line
  const timeDisplay = timeDisplayContainer
    .append("div")
    .style("display", "flex")
    .style("align-items", "center")
    .style("gap", "10px")
    .style("flex-grow", "1")
    .style("justify-content", "center");

  const yearDisplay = timeDisplay
    .append("span")
    .attr("class", "year-display")
    .style("font-weight", "600")
    .style("color", "#2e2e2e");

  const monthDisplay = timeDisplay
    .append("span")
    .attr("class", "month-display")
    .style("color", "#6b6f76");

  // Update time display font
  timeDisplay
    .append("div")
    .style("font-size", "16px")
    .style("color", "#444")
    .style("display", "flex")
    .style("justify-content", "center")
    .style("gap", "10px")
    .style("font-family", '"Roboto Mono", monospace');

  // Add play/pause button as an icon
  const playButton = timeDisplayContainer
    .append("button")
    .attr("class", "control-button")
    .style("background", "none")
    .style("border", "none")
    .style("cursor", "pointer")
    .style("padding", "0")
    .style("width", "24px")
    .style("height", "24px")
    .style("display", "flex")
    .style("align-items", "center")
    .style("justify-content", "center");

  // SVG for play/pause icon
  const buttonSvg = playButton
    .append("svg")
    .attr("width", "24")
    .attr("height", "24")
    .attr("viewBox", "0 0 24 24")
    .style("fill", "none")
    .style("stroke", "#2e2e2e")
    .style("stroke-width", "2")
    .style("stroke-linecap", "round")
    .style("stroke-linejoin", "round");

  const playPath = buttonSvg
    .append("path")
    .attr("class", "play-icon")
    .attr("d", "M5 3l14 9-14 9V3z")
    .style("fill", "#2e2e2e");

  const pauseGroup = buttonSvg
    .append("g")
    .attr("class", "pause-icon")
    .style("display", "none");

  pauseGroup
    .append("line")
    .attr("x1", "6")
    .attr("y1", "4")
    .attr("x2", "6")
    .attr("y2", "20");

  pauseGroup
    .append("line")
    .attr("x1", "18")
    .attr("y1", "4")
    .attr("x2", "18")
    .attr("y2", "20");

  // Add reset button
  const resetButton = timeDisplayContainer
    .append("button")
    .attr("class", "control-button reset-button")
    .style("background", "none")
    .style("border", "none")
    .style("cursor", "pointer")
    .style("padding", "0")
    .style("width", "24px")
    .style("height", "24px")
    .style("display", "flex")
    .style("align-items", "center")
    .style("justify-content", "center")
    .style("margin-left", "4px");

  // SVG for reset icon
  const resetSvg = resetButton
    .append("svg")
    .attr("width", "24")
    .attr("height", "24")
    .attr("viewBox", "0 0 24 24")
    .style("fill", "none")
    .style("stroke", "#2e2e2e")
    .style("stroke-width", "2")
    .style("stroke-linecap", "round")
    .style("stroke-linejoin", "round");

  // Draw circular arrow
  resetSvg
    .append("path")
    .attr("d", "M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8")
    .style("fill", "none");

  resetSvg
    .append("path")
    .attr("d", "M3 3v5h5")
    .style("fill", "none");

  let isPlaying = true; // Start playing by default
  let currentDate = new Date(2018, 0); // Start from January 2018

  // Update play button state to show pause icon initially
  playPath.style("display", "none");
  pauseGroup.style("display", null);

  const svg = d3.select(container)
    .append("svg")
    .attr("width", width)
    .attr("height", height)
    .append("g");

  // Load group layout from JSON
  const groups = await d3.json("/data/groups.json");
  Object.keys(groups).forEach(k => {
    groups[k].cnt = 0;
    // Scale down positions to better fit view
    groups[k].x = width / 2 + (groups[k].x - 400) * 0.7;
    groups[k].y = height / 2 + (groups[k].y - 400) * 0.7;
  });

  const people = {};
  let time_so_far = 0;
  const radius = 4;

  const rawData = await d3.json("/data/transitions.json");

  rawData.forEach(d => {
    d.duration = +d.duration;
    if (people[d.pid]) {
      people[d.pid].push(d);
    } else {
      people[d.pid] = [d];
    }
  });

  const nodes = Object.keys(people).map(pid => {
    const stage = people[pid][0];
    groups[stage.grp].cnt += 1;
    return {
      id: "node" + pid,
      x: groups[stage.grp].x + Math.random(),
      y: groups[stage.grp].y + Math.random(),
      r: radius,
      color: groups[stage.grp].color,
      group: stage.grp,
      timeleft: stage.duration,
      istage: 0,
      stages: people[pid]
    };
  });

  function forceCluster() {
    const strength = .12;
    let nodes;
    function force(alpha) {
      const l = alpha * strength;
      for (const d of nodes) {
        d.vx -= (d.x - groups[d.group].x) * l;
        d.vy -= (d.y - groups[d.group].y) * l;
      }
    }
    force.initialize = _ => nodes = _;
    return force;
  }

  function forceCollide() {
    const padding1 = 1, padding2 = 2;
    let nodes;
    function force() {
      const tree = d3.quadtree(nodes, d => d.x, d => d.y);
      for (const d of nodes) {
        const r = d.r;
        tree.visit((q, x1, y1, x2, y2) => {
          if (q.data && q.data !== d) {
            let x = d.x - q.data.x,
                y = d.y - q.data.y,
                l = Math.hypot(x, y),
                r = d.r + q.data.r + (d.group === q.data.group ? padding1 : padding2);
            if (l < r) {
              l = (l - r) / l * 0.5;
              d.x -= x *= l;
              d.y -= y *= l;
              q.data.x += x;
              q.data.y += y;
            }
          }
          return false;
        });
      }
    }
    force.initialize = _ => nodes = _;
    return force;
  }

  const circle = svg.append("g")
    .selectAll("circle")
    .data(nodes)
    .join("circle")
      .attr("cx", d => d.x)
      .attr("cy", d => d.y)
      .attr("fill", d => d.color);

  circle.transition()
    .delay((d, i) => i * 5)
    .duration(800)
    .attrTween("r", d => {
      const i = d3.interpolate(0, d.r);
      return t => d.r = i(t);
    });

  const simulation = d3.forceSimulation(nodes)
    .force("x", d => d3.forceX(d.x))
    .force("y", d => d3.forceY(d.y))
    .force("cluster", forceCluster())
    .force("collide", forceCollide())
    .alpha(0.09)
    .alphaDecay(0);

  simulation.on("tick", () => {
    circle
      .attr("cx", d => d.x)
      .attr("cy", d => d.y)
      .attr("fill", d => groups[d.group].color);
  });

  // Add labels with increased weight
  svg.append("g")
    .selectAll("text")
    .data(Object.entries(groups))
    .join("text")
    .attr("x", ([, g]) => g.x)
    .attr("y", ([, g]) => g.y - 30)
    .attr("text-anchor", "middle")
    .style("font-size", "13px")
    .style("fill", "#444")
    .style("font-weight", "600")
    .style("font-family", '"Roboto Mono", monospace')
    .text(([name]) => name);

  function updateTimeDisplay() {
    yearDisplay.text(currentDate.getFullYear());
    monthDisplay.text(currentDate.toLocaleDateString('en-US', { month: 'long' }));
  }

  function togglePlay() {
    isPlaying = !isPlaying;
    playPath.style("display", isPlaying ? "none" : null);
    pauseGroup.style("display", isPlaying ? null : "none");
  }

  playButton.on("click", togglePlay);

  function resetSimulation() {
    // Reset date to January 2018
    currentDate = new Date(2018, 0);
    updateTimeDisplay();

    // Reset all nodes to their initial state
    nodes.forEach(node => {
      const initialStage = node.stages[0];
      if (node.group !== initialStage.grp) {
        groups[node.group].cnt -= 1;
        groups[initialStage.grp].cnt += 1;
      }
      node.group = initialStage.grp;
      node.istage = 0;
      node.timeleft = initialStage.duration;
    });

    // Stop the animation if it's playing
    if (isPlaying) {
      togglePlay();
    }
  }

  resetButton.on("click", resetSimulation);

  function timer() {
    if (isPlaying) {
      nodes.forEach(o => {
        o.timeleft -= 1;
        if (o.timeleft === 0 && o.istage < o.stages.length - 1) {
          groups[o.group].cnt -= 1;
          o.istage += 1;
          o.group = o.stages[o.istage].grp;
          o.timeleft = o.stages[o.istage].duration;
          groups[o.group].cnt += 1;
        }
      });

      // Update the date
      currentDate.setMonth(currentDate.getMonth() + 1);
      if (currentDate > new Date(2023, 11)) { // Reset after December 2023
        currentDate = new Date(2018, 0);
      }
      updateTimeDisplay();

      time_so_far += 1;
    }
    d3.timeout(timer, 500);
  }

  // Initialize time display and start timer
  updateTimeDisplay();
  d3.timeout(timer, 500);
}
