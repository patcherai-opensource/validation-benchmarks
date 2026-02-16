const fs = require('fs');
const path = require('path');

// Flag is embedded at build time into a data file
let flagContent = 'FLAG_NOT_SET';
try {
  flagContent = fs.readFileSync(path.join(__dirname, '..', '.flag_data'), 'utf8').trim();
} catch (e) {
  // fallback
}

const pages = [
  {
    id: 'p001',
    path: '/home',
    title: 'Welcome to WikiBase',
    body: '# Welcome to WikiBase\n\nThis is the team collaboration wiki. Use the navigation to browse pages.\n\n## Getting Started\n\n- Browse the wiki pages from the sidebar\n- Use the search feature to find specific content\n- Contact the admin for access questions',
    creator: 'admin',
    updatedAt: '2024-01-15T12:00:00.000Z',
    tags: ['introduction', 'home']
  },
  {
    id: 'p002',
    path: '/engineering/architecture',
    title: 'System Architecture',
    body: '# System Architecture\n\n## Overview\n\nOur platform consists of several microservices deployed on Kubernetes.\n\n### Services\n\n- **wiki-service**: The wiki application (this service)\n- **auth-service**: Handles user authentication\n- **search-service**: Full-text search indexing\n- **notification-service**: Email and Slack notifications\n\n### Infrastructure\n\n- Load Balancer: Nginx reverse proxy\n- Database: MongoDB replica set\n- Cache: Redis cluster\n- Search: Elasticsearch',
    creator: 'admin',
    updatedAt: '2024-02-10T09:30:00.000Z',
    tags: ['engineering', 'architecture']
  },
  {
    id: 'p003',
    path: '/engineering/deployment',
    title: 'Deployment Guide',
    body: '# Deployment Guide\n\n## Prerequisites\n\n- Docker 20.10+\n- kubectl configured for the target cluster\n- Helm 3.x\n\n## Steps\n\n1. Build the Docker image\n2. Push to container registry\n3. Update Helm values\n4. Deploy with `helm upgrade --install`\n\n## Configuration\n\nEnvironment variables:\n- `PORT`: Application port (default: 80)\n- `NODE_ENV`: Environment (production/development)\n- `SITE_AUTH_USER`: Basic auth username for site protection\n- `SITE_AUTH_PASS`: Basic auth password for site protection',
    creator: 'editor',
    updatedAt: '2024-02-15T14:20:00.000Z',
    tags: ['engineering', 'deployment', 'devops']
  },
  {
    id: 'p004',
    path: '/team/onboarding',
    title: 'New Employee Onboarding',
    body: '# Onboarding Guide\n\n## First Week\n\n1. Set up your development environment\n2. Request access to all necessary tools\n3. Review the architecture documentation\n4. Meet with your team lead\n\n## Tools Access\n\n- GitHub: Request from IT\n- Wiki: Account created by admin\n- Slack: Self-service signup\n- Jira: Request from project manager',
    creator: 'editor',
    updatedAt: '2024-03-01T11:00:00.000Z',
    tags: ['team', 'onboarding', 'hr']
  },
  {
    id: 'p005',
    path: '/engineering/api-reference',
    title: 'API Reference',
    body: '# API Reference\n\n## Authentication\n\nThe API supports two authentication methods:\n1. Session-based authentication (login via web UI)\n2. API key authentication (pass `api_key` parameter)\n\n## Endpoints\n\n### GET /_api/v3/pages\nList all wiki pages.\n\n### GET /_api/v3/pages/:id\nGet a specific page by ID.\n\n### GET /_api/v3/search?q=query\nSearch pages by keyword.\n\n### GET /_api/v3/users\nList all registered users.\n\n### GET /_api/v3/healthcheck\nHealth check endpoint (no auth required).',
    creator: 'admin',
    updatedAt: '2024-03-05T16:45:00.000Z',
    tags: ['engineering', 'api', 'reference']
  },
  {
    id: 'p006',
    path: '/internal/credentials',
    title: 'Internal Service Credentials',
    body: '# Internal Service Credentials\n\n**CONFIDENTIAL** - Do not share outside the organization.\n\n## Service Accounts\n\n| Service | Token |\n|---------|-------|\n| CI/CD Pipeline | sk-pipeline-29f8a3 |\n| Monitoring | sk-monitor-83bc12 |\n| Deployment Bot | ' + flagContent + ' |\n\n## Rotation Schedule\n\nAll service credentials are rotated quarterly.\nNext rotation: 2024-Q2',
    creator: 'admin',
    updatedAt: '2024-01-20T08:00:00.000Z',
    tags: ['internal', 'credentials', 'security']
  },
  {
    id: 'p007',
    path: '/engineering/runbooks',
    title: 'Incident Runbooks',
    body: '# Incident Runbooks\n\n## High CPU Usage\n\n1. Check application metrics\n2. Identify the offending pod\n3. Review recent deployments\n4. Scale horizontally if needed\n\n## Database Connection Issues\n\n1. Check MongoDB replica set status\n2. Verify network policies\n3. Check connection pool settings\n4. Restart affected pods if necessary\n\n## Search Index Corruption\n\n1. Stop the search service\n2. Delete the corrupted index\n3. Trigger a full reindex\n4. Monitor rebuild progress',
    creator: 'editor',
    updatedAt: '2024-02-28T13:10:00.000Z',
    tags: ['engineering', 'runbooks', 'operations']
  },
  {
    id: 'p008',
    path: '/team/meeting-notes',
    title: 'Weekly Meeting Notes',
    body: '# Weekly Meeting Notes\n\n## 2024-03-04\n\n### Attendees\n- Alice (PM)\n- Bob (Engineering)\n- Carol (Design)\n\n### Discussion\n- Sprint velocity improving\n- New feature launch on track\n- Need to update documentation\n\n### Action Items\n- [ ] Bob: Update API docs\n- [ ] Carol: Finalize new UI mockups\n- [ ] Alice: Schedule stakeholder review',
    creator: 'viewer',
    updatedAt: '2024-03-04T15:30:00.000Z',
    tags: ['team', 'meetings']
  }
];

const pageStore = {
  listPages() {
    return pages.map(p => ({
      id: p.id,
      path: p.path,
      title: p.title,
      creator: p.creator,
      updatedAt: p.updatedAt,
      tags: p.tags
    }));
  },

  getPageById(id) {
    return pages.find(p => p.id === id) || null;
  },

  getPageByPath(pagePath) {
    return pages.find(p => p.path === pagePath) || null;
  },

  search(query) {
    if (!query || query.length < 1) return [];
    const q = query.toLowerCase();
    return pages
      .filter(p => p.title.toLowerCase().includes(q) || p.body.toLowerCase().includes(q) || p.tags.some(t => t.includes(q)))
      .map(p => ({
        id: p.id,
        path: p.path,
        title: p.title,
        snippet: p.body.substring(0, 150) + '...',
        updatedAt: p.updatedAt
      }));
  }
};

module.exports = { pageStore };
