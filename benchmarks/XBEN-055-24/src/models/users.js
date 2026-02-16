const crypto = require('crypto');

const userStore = [
  {
    id: 'u001',
    username: 'admin',
    password: crypto.randomBytes(32).toString('hex'),
    name: 'Wiki Administrator',
    admin: true,
    status: 'active',
    apiToken: crypto.randomBytes(32).toString('hex'),
    sessionToken: crypto.randomBytes(32).toString('hex'),
    createdAt: '2023-01-15T08:00:00.000Z'
  },
  {
    id: 'u002',
    username: 'editor',
    password: crypto.randomBytes(32).toString('hex'),
    name: 'Content Editor',
    admin: false,
    status: 'active',
    apiToken: crypto.randomBytes(32).toString('hex'),
    sessionToken: crypto.randomBytes(32).toString('hex'),
    createdAt: '2023-02-20T10:30:00.000Z'
  },
  {
    id: 'u003',
    username: 'viewer',
    password: crypto.randomBytes(32).toString('hex'),
    name: 'Read Only User',
    admin: false,
    status: 'active',
    apiToken: crypto.randomBytes(32).toString('hex'),
    sessionToken: crypto.randomBytes(32).toString('hex'),
    createdAt: '2023-03-10T14:15:00.000Z'
  }
];

function authenticate(username, password) {
  return userStore.find(u => u.username === username && u.password === password) || null;
}

function findByApiToken(token) {
  return userStore.find(u => u.apiToken === token) || null;
}

function findBySessionToken(token) {
  return userStore.find(u => u.sessionToken === token) || null;
}

function listUsers() {
  return userStore.map(u => ({
    id: u.id,
    username: u.username,
    name: u.name,
    status: u.status,
    admin: u.admin,
    createdAt: u.createdAt
  }));
}

module.exports = { authenticate, findByApiToken, findBySessionToken, listUsers };
