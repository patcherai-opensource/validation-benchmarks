<?php $pageTitle = 'Dashboard'; require __DIR__ . '/layout.php'; ?>

<nav class="navbar">
    <a href="/" class="navbar-brand">Task<span>Flow</span></a>
    <ul class="navbar-nav">
        <li><a href="/" class="active">Dashboard</a></li>
        <li><a href="/tasks">Tasks</a></li>
        <?php if ($user): ?>
            <li><a href="/profile">Profile</a></li>
        <?php endif; ?>
    </ul>
    <div class="navbar-user">
        <?php if ($user): ?>
            <div class="avatar"><?php echo strtoupper(substr($user['name'], 0, 1)); ?></div>
            <span><?php echo htmlspecialchars($user['name']); ?></span>
            <a href="/logout" class="btn btn-sm btn-secondary">Logout</a>
        <?php else: ?>
            <a href="/login" class="btn btn-sm btn-primary">Sign In</a>
        <?php endif; ?>
    </div>
</nav>

<div class="container">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
        <div>
            <h1 style="font-size: 1.5rem; color: #1a1a2e;">Dashboard</h1>
            <p style="color: #888; font-size: 0.85rem; margin-top: 0.25rem;">Welcome back<?php echo $user ? ', ' . htmlspecialchars($user['name']) : ''; ?>. Here's your overview.</p>
        </div>
    </div>

    <div class="stats-grid">
        <div class="stat-card">
            <div class="label">Total Tasks</div>
            <div class="value"><?php echo count($tasks); ?></div>
            <div class="change">+2 this week</div>
        </div>
        <div class="stat-card">
            <div class="label">Completed</div>
            <div class="value"><?php echo count(array_filter($tasks, function($t) { return $t['status'] === 'completed'; })); ?></div>
            <div class="change">1 today</div>
        </div>
        <div class="stat-card">
            <div class="label">In Progress</div>
            <div class="value"><?php echo count(array_filter($tasks, function($t) { return $t['status'] === 'in_progress'; })); ?></div>
        </div>
        <div class="stat-card">
            <div class="label">Pending</div>
            <div class="value"><?php echo count(array_filter($tasks, function($t) { return $t['status'] === 'pending'; })); ?></div>
        </div>
    </div>

    <div class="card">
        <h2>Recent Tasks</h2>
        <table>
            <thead>
                <tr>
                    <th>Task</th>
                    <th>Status</th>
                    <th>Priority</th>
                    <th>Assigned</th>
                    <th>Due Date</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($tasks as $task): ?>
                <tr>
                    <td><?php echo htmlspecialchars($task['title']); ?></td>
                    <td>
                        <?php
                        $statusClass = 'badge-pending';
                        $statusLabel = 'Pending';
                        if ($task['status'] === 'in_progress') { $statusClass = 'badge-progress'; $statusLabel = 'In Progress'; }
                        elseif ($task['status'] === 'completed') { $statusClass = 'badge-completed'; $statusLabel = 'Completed'; }
                        ?>
                        <span class="badge <?php echo $statusClass; ?>"><?php echo $statusLabel; ?></span>
                    </td>
                    <td>
                        <?php
                        $prioClass = 'badge-medium';
                        if ($task['priority'] === 'critical') $prioClass = 'badge-critical';
                        elseif ($task['priority'] === 'high') $prioClass = 'badge-high';
                        elseif ($task['priority'] === 'low') $prioClass = 'badge-low';
                        ?>
                        <span class="badge <?php echo $prioClass; ?>"><?php echo ucfirst($task['priority']); ?></span>
                    </td>
                    <td><?php echo htmlspecialchars($task['assigned']); ?></td>
                    <td><?php echo htmlspecialchars($task['due']); ?></td>
                </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    </div>
</div>

<div class="footer">
    <p>&copy; 2024 TaskFlow. All rights reserved. | Version 5.6.28</p>
</div>

</body>
</html>