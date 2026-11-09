#!/usr/bin/env node
'use strict';

const fs = require('fs');

const inputPath = process.argv[2];
const outputPath = process.argv[3];

if (!inputPath || !outputPath) {
  process.stderr.write('Usage: node ua-tour-analyze.js <input.json> <output.json>\n');
  process.exit(1);
}

let data;
try {
  data = JSON.parse(fs.readFileSync(inputPath, 'utf8'));
} catch (e) {
  process.stderr.write('Failed to parse input JSON: ' + e.message + '\n');
  process.exit(1);
}

const { nodes, edges, layers } = data;

// Build lookup maps
const nodeMap = {};
for (const n of nodes) {
  nodeMap[n.id] = n;
}

// A. Fan-In: count edges pointing TO each node
const fanIn = {};
const fanOut = {};
for (const n of nodes) {
  fanIn[n.id] = 0;
  fanOut[n.id] = 0;
}
for (const e of edges) {
  if (fanIn[e.target] !== undefined) fanIn[e.target]++;
  if (fanOut[e.source] !== undefined) fanOut[e.source]++;
}

const fanInRanking = Object.entries(fanIn)
  .sort((a, b) => b[1] - a[1])
  .slice(0, 20)
  .map(([id, count]) => ({ id, fanIn: count, name: nodeMap[id] ? nodeMap[id].name : id }));

const fanOutRanking = Object.entries(fanOut)
  .sort((a, b) => b[1] - a[1])
  .slice(0, 20)
  .map(([id, count]) => ({ id, fanOut: count, name: nodeMap[id] ? nodeMap[id].name : id }));

// B. Entry Point Candidates
const totalNodes = nodes.length;
const fanOutValues = Object.values(fanOut).sort((a, b) => b - a);
const top10PctThreshold = fanOutValues[Math.floor(totalNodes * 0.10)] || 0;
const fanInValues = Object.values(fanIn).sort((a, b) => a - b);
const bottom25PctThreshold = fanInValues[Math.floor(totalNodes * 0.25)] || 0;

const entryNamePatterns = [
  'index.ts','index.js','main.ts','main.js','app.ts','app.js',
  'server.ts','server.js','mod.rs','main.go','main.py','main.rs',
  'manage.py','app.py','wsgi.py','asgi.py','run.py','__main__.py',
  'Application.java','Main.java','Program.cs','config.ru','index.php',
  'App.swift','Application.kt','main.cpp','main.c'
];

function scoreNode(node) {
  let score = 0;
  const type = node.type;
  const name = node.name;
  const path = node.filePath || '';

  if (type === 'document') {
    if (name === 'README.md' && !path.includes('/')) score += 5;
    else if (name.endsWith('.md') && !path.includes('/')) score += 2;
    return score;
  }

  if (type === 'file') {
    if (entryNamePatterns.includes(name)) score += 3;
    const depth = path.split('/').length;
    if (depth <= 2) score += 1;
    if (fanOut[node.id] >= top10PctThreshold && fanOut[node.id] > 0) score += 1;
    if (fanIn[node.id] <= bottom25PctThreshold) score += 1;
  }

  return score;
}

const scored = nodes.map(n => ({
  id: n.id,
  score: scoreNode(n),
  name: n.name,
  type: n.type,
  summary: n.summary || ''
})).sort((a, b) => b.score - a.score);

const entryPointCandidates = scored.slice(0, 5);

// C. BFS from top code entry point (skip documents)
const codeEntry = scored.find(n => n.type === 'file');
const bfsStart = codeEntry ? codeEntry.id : null;

const bfsResult = { startNode: bfsStart, order: [], depthMap: {}, byDepth: {} };

if (bfsStart) {
  // Build adjacency list for imports/calls edges only
  const adj = {};
  for (const n of nodes) adj[n.id] = [];
  for (const e of edges) {
    if (e.type === 'imports' || e.type === 'calls') {
      if (adj[e.source]) adj[e.source].push(e.target);
    }
  }

  const visited = new Set();
  const queue = [{ id: bfsStart, depth: 0 }];
  visited.add(bfsStart);

  while (queue.length > 0) {
    const { id, depth } = queue.shift();
    bfsResult.order.push(id);
    bfsResult.depthMap[id] = depth;
    if (!bfsResult.byDepth[depth]) bfsResult.byDepth[depth] = [];
    bfsResult.byDepth[depth].push(id);

    for (const neighbor of (adj[id] || [])) {
      if (!visited.has(neighbor)) {
        visited.add(neighbor);
        queue.push({ id: neighbor, depth: depth + 1 });
      }
    }
  }
}

// D. Non-Code File Inventory
const nonCodeFiles = { documentation: [], infrastructure: [], data: [], config: [] };
for (const n of nodes) {
  if (n.type === 'document') {
    nonCodeFiles.documentation.push({ id: n.id, name: n.name, type: n.type, summary: n.summary || '' });
  } else if (['service','pipeline','resource'].includes(n.type)) {
    nonCodeFiles.infrastructure.push({ id: n.id, name: n.name, type: n.type, summary: n.summary || '' });
  } else if (['table','schema','endpoint'].includes(n.type)) {
    nonCodeFiles.data.push({ id: n.id, name: n.name, type: n.type, summary: n.summary || '' });
  } else if (n.type === 'config') {
    nonCodeFiles.config.push({ id: n.id, name: n.name, type: n.type, summary: n.summary || '' });
  }
}

// E. Tightly Coupled Clusters
// Find bidirectional pairs
const edgeSet = new Set();
for (const e of edges) {
  edgeSet.add(e.source + '|||' + e.target);
}

const biPairs = [];
for (const e of edges) {
  const reverse = e.target + '|||' + e.source;
  if (edgeSet.has(reverse) && e.source < e.target) {
    biPairs.push([e.source, e.target]);
  }
}

// Build clusters by expanding bidirectional pairs
const clusters = [];
const clusterMembership = {};

for (const [a, b] of biPairs) {
  let added = false;
  for (const cluster of clusters) {
    if (cluster.includes(a) || cluster.includes(b)) {
      if (!cluster.includes(a)) cluster.push(a);
      if (!cluster.includes(b)) cluster.push(b);
      added = true;
      break;
    }
  }
  if (!added) clusters.push([a, b]);
}

// Expand clusters: add nodes connecting to 2+ cluster members
for (const cluster of clusters) {
  for (const n of nodes) {
    if (cluster.includes(n.id)) continue;
    let connections = 0;
    for (const m of cluster) {
      if (edgeSet.has(n.id + '|||' + m) || edgeSet.has(m + '|||' + n.id)) connections++;
    }
    if (connections >= 2 && cluster.length < 5) cluster.push(n.id);
  }
}

// Count edges within each cluster
const rankedClusters = clusters.map(clusterNodes => {
  let edgeCount = 0;
  for (let i = 0; i < clusterNodes.length; i++) {
    for (let j = 0; j < clusterNodes.length; j++) {
      if (i !== j && edgeSet.has(clusterNodes[i] + '|||' + clusterNodes[j])) edgeCount++;
    }
  }
  return { nodes: clusterNodes, edgeCount };
}).sort((a, b) => b.edgeCount - a.edgeCount).slice(0, 10);

// F. Node Summary Index
const nodeSummaryIndex = {};
for (const n of nodes) {
  nodeSummaryIndex[n.id] = { name: n.name, type: n.type, summary: n.summary || '' };
}

// G. Layer List
const layerInfo = {
  count: layers.length,
  list: layers.map(l => ({ id: l.id, name: l.name, description: l.description }))
};

// Final output
const output = {
  scriptCompleted: true,
  entryPointCandidates,
  fanInRanking,
  fanOutRanking,
  bfsTraversal: bfsResult,
  nonCodeFiles,
  clusters: rankedClusters,
  layers: layerInfo,
  nodeSummaryIndex,
  totalNodes: nodes.length,
  totalEdges: edges.length
};

try {
  fs.writeFileSync(outputPath, JSON.stringify(output, null, 2), 'utf8');
} catch (e) {
  process.stderr.write('Failed to write output: ' + e.message + '\n');
  process.exit(1);
}

process.exit(0);
