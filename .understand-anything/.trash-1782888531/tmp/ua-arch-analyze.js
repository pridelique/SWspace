#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');

const inputPath = process.argv[2];
const outputPath = process.argv[3];

if (!inputPath || !outputPath) {
  console.error('Usage: node ua-arch-analyze.js <input.json> <output.json>');
  process.exit(1);
}

let input;
try {
  input = JSON.parse(fs.readFileSync(inputPath, 'utf8'));
} catch (e) {
  console.error('Failed to read/parse input:', e.message);
  process.exit(1);
}

const { fileNodes, importEdges, allEdges } = input;

// ─── A. Directory Grouping ────────────────────────────────────────────────────

function getCommonPrefix(paths) {
  if (!paths.length) return '';
  const parts = paths[0].split('/');
  let prefix = [];
  for (let i = 0; i < parts.length - 1; i++) {
    const seg = parts[i];
    if (paths.every(p => p.split('/')[i] === seg)) {
      prefix.push(seg);
    } else break;
  }
  return prefix.length ? prefix.join('/') + '/' : '';
}

const allPaths = fileNodes.map(n => n.filePath);
const commonPrefix = getCommonPrefix(allPaths);

function getDirectoryGroup(filePath) {
  let rel = filePath;
  if (commonPrefix && rel.startsWith(commonPrefix)) {
    rel = rel.slice(commonPrefix.length);
  }
  const segs = rel.split('/');
  if (segs.length === 1) return 'root';
  return segs[0];
}

const directoryGroups = {};
for (const node of fileNodes) {
  const grp = getDirectoryGroup(node.filePath);
  if (!directoryGroups[grp]) directoryGroups[grp] = [];
  directoryGroups[grp].push(node.id);
}

// ─── B. Node Type Grouping ────────────────────────────────────────────────────

const nodeTypeGroups = {};
for (const node of fileNodes) {
  const t = node.type || 'file';
  if (!nodeTypeGroups[t]) nodeTypeGroups[t] = [];
  nodeTypeGroups[t].push(node.id);
}

// ─── C. Import Adjacency / Fan-in / Fan-out ──────────────────────────────────

const fanOut = {};
const fanIn = {};
for (const node of fileNodes) {
  fanOut[node.id] = 0;
  fanIn[node.id] = 0;
}
for (const edge of importEdges) {
  if (fanOut[edge.source] !== undefined) fanOut[edge.source]++;
  if (fanIn[edge.target] !== undefined) fanIn[edge.target]++;
}

// ─── D. Cross-Category Dependency Analysis ───────────────────────────────────

const nodeTypeMap = {};
for (const node of fileNodes) nodeTypeMap[node.id] = node.type || 'file';

const crossCategoryMap = {};
for (const edge of allEdges) {
  const fromType = nodeTypeMap[edge.source] || 'unknown';
  const toType = nodeTypeMap[edge.target] || 'unknown';
  if (fromType === toType) continue;
  const key = `${fromType}|${toType}|${edge.type}`;
  crossCategoryMap[key] = (crossCategoryMap[key] || 0) + 1;
}
const crossCategoryEdges = Object.entries(crossCategoryMap).map(([key, count]) => {
  const [fromType, toType, edgeType] = key.split('|');
  return { fromType, toType, edgeType, count };
});

// ─── E. Inter-Group Import Frequency ─────────────────────────────────────────

const nodeGroupMap = {};
for (const node of fileNodes) {
  nodeGroupMap[node.id] = getDirectoryGroup(node.filePath);
}

const interGroupMap = {};
for (const edge of importEdges) {
  const fromGrp = nodeGroupMap[edge.source];
  const toGrp = nodeGroupMap[edge.target];
  if (!fromGrp || !toGrp || fromGrp === toGrp) continue;
  const key = `${fromGrp}|${toGrp}`;
  interGroupMap[key] = (interGroupMap[key] || 0) + 1;
}
const interGroupImports = Object.entries(interGroupMap).map(([key, count]) => {
  const [from, to] = key.split('|');
  return { from, to, count };
}).sort((a, b) => b.count - a.count);

// ─── F. Intra-Group Import Density ───────────────────────────────────────────

const intraGroupDensity = {};
for (const grp of Object.keys(directoryGroups)) {
  const members = new Set(directoryGroups[grp]);
  let internal = 0, total = 0;
  for (const edge of importEdges) {
    const fromInGrp = members.has(edge.source);
    const toInGrp = members.has(edge.target);
    if (fromInGrp || toInGrp) total++;
    if (fromInGrp && toInGrp) internal++;
  }
  intraGroupDensity[grp] = {
    internalEdges: internal,
    totalEdges: total,
    density: total > 0 ? Math.round((internal / total) * 100) / 100 : 0
  };
}

// ─── G. Directory Pattern Matching ───────────────────────────────────────────

const dirPatterns = {
  routes: 'api', api: 'api', controllers: 'api', endpoints: 'api', handlers: 'api',
  serializers: 'api', controller: 'api', routers: 'api', blueprints: 'api',
  services: 'service', core: 'service', lib: 'service', domain: 'service', logic: 'service',
  composables: 'service', signals: 'service', mailers: 'service', jobs: 'service', channels: 'service',
  models: 'data', db: 'data', data: 'data', persistence: 'data', repository: 'data',
  entities: 'data', migrations: 'data', entity: 'data', sql: 'data', database: 'data', schema: 'data',
  components: 'ui', views: 'ui', pages: 'ui', ui: 'ui', layouts: 'ui', screens: 'ui',
  middleware: 'middleware', plugins: 'middleware', interceptors: 'middleware', guards: 'middleware',
  utils: 'utility', helpers: 'utility', common: 'utility', shared: 'utility', tools: 'utility',
  pkg: 'utility', templatetags: 'utility',
  config: 'config', constants: 'config', env: 'config', settings: 'config',
  management: 'config', commands: 'config',
  __tests__: 'test', test: 'test', tests: 'test', spec: 'test', specs: 'test',
  types: 'types', interfaces: 'types', schemas: 'types', contracts: 'types', dtos: 'types',
  dto: 'types', request: 'types', response: 'types',
  hooks: 'hooks',
  store: 'state', state: 'state', reducers: 'state', actions: 'state', slices: 'state',
  assets: 'assets', static: 'assets', public: 'assets',
  cmd: 'entry', bin: 'entry',
  internal: 'service',
  docs: 'documentation', documentation: 'documentation', wiki: 'documentation',
  deploy: 'infrastructure', deployment: 'infrastructure', infra: 'infrastructure',
  infrastructure: 'infrastructure', k8s: 'infrastructure', kubernetes: 'infrastructure',
  helm: 'infrastructure', charts: 'infrastructure', terraform: 'infrastructure',
  tf: 'infrastructure', docker: 'infrastructure',
  '.github': 'ci-cd', '.gitlab': 'ci-cd', '.circleci': 'ci-cd',
  templates: 'ui', accounts: 'api', portal: 'api', app: 'ui', components: 'ui'
};

const filePatterns = [
  { pattern: /\.(test|spec)\.[^.]+$/, label: 'test' },
  { pattern: /^test_.*\.py$/, label: 'test' },
  { pattern: /_test\.go$/, label: 'test' },
  { pattern: /Test\.java$/, label: 'test' },
  { pattern: /\.d\.ts$/, label: 'types' },
  { pattern: /^(index\.(ts|js)|__init__\.py)$/, label: 'entry' },
  { pattern: /^manage\.py$/, label: 'entry' },
  { pattern: /^(wsgi|asgi)\.py$/, label: 'config' },
  { pattern: /^main\.(go|rs)$/, label: 'entry' },
  { pattern: /^lib\.rs$/, label: 'entry' },
  { pattern: /^(Application\.java|Program\.cs)$/, label: 'entry' },
  { pattern: /^config\.ru$/, label: 'entry' },
  { pattern: /^(Cargo\.toml|go\.mod|Gemfile|pom\.xml|build\.gradle|composer\.json)$/, label: 'config' },
  { pattern: /^(Dockerfile|docker-compose\..+)$/, label: 'infrastructure' },
  { pattern: /\.(tf|tfvars)$/, label: 'infrastructure' },
  { pattern: /^Makefile$/, label: 'infrastructure' },
  { pattern: /\.(graphql|gql|proto)$/, label: 'types' },
  { pattern: /\.(md|rst)$/, label: 'documentation' },
  { pattern: /\.sql$/, label: 'data' }
];

const patternMatches = {};
for (const grp of Object.keys(directoryGroups)) {
  patternMatches[grp] = dirPatterns[grp.toLowerCase()] || 'unknown';
}

// Also classify individual files by file-level patterns
const filePatternMatches = {};
for (const node of fileNodes) {
  const fname = node.name;
  for (const { pattern, label } of filePatterns) {
    if (pattern.test(fname)) {
      filePatternMatches[node.id] = label;
      break;
    }
  }
}

// ─── H. Deployment Topology ───────────────────────────────────────────────────

const allFilePaths = fileNodes.map(n => n.filePath);
const deploymentTopology = {
  hasDockerfile: allFilePaths.some(p => /Dockerfile/.test(p)),
  hasCompose: allFilePaths.some(p => /docker-compose/.test(p)),
  hasK8s: allFilePaths.some(p => /\.(yaml|yml)$/.test(p) && /k8s|kubernetes|manifest/.test(p)),
  hasTerraform: allFilePaths.some(p => /\.(tf|tfvars)$/.test(p)),
  hasCI: allFilePaths.some(p => /\.github|\.gitlab|Jenkinsfile|\.circleci/.test(p)),
  infraFiles: allFilePaths.filter(p =>
    /Dockerfile|docker-compose|\.tf$|\.tfvars$|Makefile|\.github\/workflows/.test(p)
  )
};

// ─── I. Data Pipeline Detection ───────────────────────────────────────────────

const dataPipeline = {
  schemaFiles: allFilePaths.filter(p => /\.(graphql|gql|proto|sql)$/.test(p) || /schema/.test(p)),
  migrationFiles: allFilePaths.filter(p => /migrations?\//.test(p) && /\.py$/.test(p) && !/^__init__/.test(path.basename(p))),
  dataModelFiles: allFilePaths.filter(p => /models\.py$/.test(p)),
  apiHandlerFiles: allFilePaths.filter(p => /views\.py$|urls\.py$/.test(p))
};

// ─── J. Documentation Coverage ───────────────────────────────────────────────

const docFiles = fileNodes.filter(n => n.type === 'document' || /\.(md|rst)$/i.test(n.filePath));
const allGroups = Object.keys(directoryGroups);
const groupsWithDocs = allGroups.filter(grp => {
  const members = directoryGroups[grp];
  return members.some(id => docFiles.find(d => d.id === id));
});

const docCoverage = {
  groupsWithDocs: groupsWithDocs.length,
  totalGroups: allGroups.length,
  coverageRatio: Math.round((groupsWithDocs.length / allGroups.length) * 100) / 100,
  undocumentedGroups: allGroups.filter(g => !groupsWithDocs.includes(g))
};

// ─── K. Dependency Direction ──────────────────────────────────────────────────

const pairCounts = {};
for (const { from, to, count } of interGroupImports) {
  const fwd = `${from}|${to}`;
  const rev = `${to}|${from}`;
  if (!pairCounts[fwd]) pairCounts[fwd] = 0;
  pairCounts[fwd] += count;
}

const dependencyDirection = [];
const seen = new Set();
for (const { from, to } of interGroupImports) {
  const fwd = `${from}|${to}`;
  const rev = `${to}|${from}`;
  if (seen.has(fwd) || seen.has(rev)) continue;
  seen.add(fwd);
  seen.add(rev);
  const fwdCount = pairCounts[fwd] || 0;
  const revCount = pairCounts[rev] || 0;
  if (fwdCount >= revCount) {
    dependencyDirection.push({ dependent: from, dependsOn: to });
  } else {
    dependencyDirection.push({ dependent: to, dependsOn: from });
  }
}

// ─── File Stats ───────────────────────────────────────────────────────────────

const filesPerGroup = {};
for (const [grp, ids] of Object.entries(directoryGroups)) {
  filesPerGroup[grp] = ids.length;
}
const nodeTypeCounts = {};
for (const node of fileNodes) {
  const t = node.type || 'file';
  nodeTypeCounts[t] = (nodeTypeCounts[t] || 0) + 1;
}

const fileStats = {
  totalFileNodes: fileNodes.length,
  filesPerGroup,
  nodeTypeCounts
};

// ─── Assemble Output ──────────────────────────────────────────────────────────

const result = {
  scriptCompleted: true,
  commonPrefix,
  directoryGroups,
  nodeTypeGroups,
  crossCategoryEdges,
  interGroupImports,
  intraGroupDensity,
  patternMatches,
  filePatternMatches,
  deploymentTopology,
  dataPipeline,
  docCoverage,
  dependencyDirection,
  fileStats,
  fileFanIn: fanIn,
  fileFanOut: fanOut
};

try {
  fs.writeFileSync(outputPath, JSON.stringify(result, null, 2), 'utf8');
  console.log('Analysis complete. Output written to:', outputPath);
  console.log('Total file nodes:', fileNodes.length);
  console.log('Directory groups:', Object.keys(directoryGroups).join(', '));
} catch (e) {
  console.error('Failed to write output:', e.message);
  process.exit(1);
}
