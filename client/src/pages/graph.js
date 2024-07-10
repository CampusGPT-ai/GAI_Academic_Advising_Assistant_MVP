import React, { useRef, useEffect, useState } from 'react';
import * as d3 from 'd3';
import sampleData from '../model/graph/sample_data.json';
import sampleNodes from '../model/graph/sample_nodes.json';

const ConstellationGraph = () => {
  const svgRef = useRef();
  const [selectedNode, setSelectedNode] = useState(null);

  const nodes = sampleNodes;

  const links = sampleData;

  useEffect(() => {
    const width = 600; //screen.availWidth; // total width and height of the viz
    const height = 600; //screen.availHeight;

    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height)
      .append('g')
      //.call(d3.zoom().on('zoom', handleZoomSimple))

    // Color scale based on node count
    const colorScale = d3.scaleSequential(d3.interpolateBlues)
      .domain([0, d3.max(nodes, d => d.count)]);

    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink()
              .id(d => d.id)
              .distance(100)
              .links(links))
      .force('charge', d3.forceManyBody().strength(-20))
      .force('center', d3.forceCenter(width / 2, height / 2));

    const link = svg
      .selectAll('line')
      .data(links)
      .enter().append('line')
      .attr('class', 'link')
      .attr('stroke-width', d => d.value/10) // Adjust stroke width for visibility
      .attr('stroke', 'black'); // Set stroke color to black

    const node = svg
      .selectAll('circle')
      .data(nodes)
      .enter().append('circle')
      .attr('class', 'node')
      .attr('r', d => d.count === 0 ? 5 : Math.sqrt(d.count) + 5) // Adjust size
      .attr('fill', d => d.count === 0 ? 'gray' : colorScale(d.count)) // Adjust color
      .on('click', handleClick) // Add click event listener
      .call(d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended));

    node
      .append('title')
      .text(d => d.id);

    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);

      node
        .attr('cx', d => d.x)
        .attr('cy', d => d.y);
    });

    function handleZoomSimple(event) {
      svg.attr('transform', event.transform);
    }

    function handleClick(event, d) {
      console.log(d);

      const svg = d3.select(svgRef.current)
      const g = svg.select('.nodes');

      console.log(svg.node());
      const transform = d3.zoomTransform(svg);
      const x = width / 2 - d.x * transform.k;
      const y = height / 2 - d.y * transform.k;

      console.log(x, y);

      svg.transition().style("fill", "red");
        //.duration(100)
       // .call(
          //d3.zoom().transform,
          //d3.zoomIdentity.translate(x, y).scale(transform.k)
        //);

    }


    function handleZoom(event) {
      const { transform } = event;
      svg.attr('transform', transform);
      node.attr('r', d => {
        const distance = Math.hypot(transform.x - d.x, transform.y - d.y);
        return distance < 200 ? Math.sqrt(d.count) + 5 : 0; // Adjust radius based on distance
      });
      
      node.attr('opacity', d => {
        const distance = Math.hypot(transform.x - d.x, transform.y - d.y);
        return distance < 200 ? 1 : 0; // Adjust opacity based on distance
      });

      // Adjust link opacity based on zoom level and distance from the center
      link.attr('opacity', d => {
        const distanceSource = Math.hypot(transform.x - d.source.x, transform.y - d.source.y);
        const distanceTarget = Math.hypot(transform.x - d.target.x, transform.y - d.target.y);
        return (distanceSource < 200 && distanceTarget < 200) ? 1 : 0; // Adjust opacity of links based on distance
      });
    }

    function dragstarted(event, d) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event, d) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event, d) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }
  }, [nodes, links]);

  useEffect(() => {
    if (selectedNode) {
    }
  }, [selectedNode]);

  return React.createElement('svg', { ref: svgRef });
};

export default ConstellationGraph;