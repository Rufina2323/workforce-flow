
export async function createTransitionChart() {
  const container = document.getElementById("transition-chart");
  if (!container) return;

  const width = container.clientWidth;
  const height = 600;
  container.innerHTML = "";

  const svg = d3.select(container)
      .append("svg")
      .attr("width", width)
      .attr("height", height)
    .append("g");

  // Load group layout from JSON
  const groups = await d3.json("/data/groups_circle_layout.json");
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

  // Add labels
  svg.append("g")
    .selectAll("text")
    .data(Object.entries(groups))
    .join("text")
    .attr("x", ([, g]) => g.x)
    .attr("y", ([, g]) => g.y - 30)
    .attr("text-anchor", "middle")
    .style("font-size", "13px")
    .style("fill", "#444")
    .style("font-weight", 500)
    .text(([name]) => name);

  function timer() {
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

    time_so_far += 1;
    d3.timeout(timer, 500);
  }

  d3.timeout(timer, 500);
}
