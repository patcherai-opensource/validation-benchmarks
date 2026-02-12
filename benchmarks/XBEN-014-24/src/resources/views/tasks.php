<?php $pageTitle = 'Tasks'; require __DIR__ . '/layout.php'; ?>

<nav class="navbar">
    <a href="/" class="navbar-brand">Task<span>Flow</span></a>
    <ul class="navbar-nav">
        <li><a href="/">Dashboard</a></li>
        <li><a href="/tasks" class="active">Tasks</a></li>
        <li><a href="/profile">Profile</a></li>
    </ul>
    <div class="navbar-user">
        <div class="avatar"><?php echo strtoupper(substr($user['name'], 0, 1)); ?></div>
        <span><?php echo htmlspecialchars($user['name']); ?></span>
        <a href="/logout" class="btn btn-sm btn-secondary">Logout</a>
    </div>
</nav>

<div class="container">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
        <h1 style="font-size: 1.5rem; color: #1a1a2e;">Tasks</h1>
    </div>

    <div class="card">
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Task</th>
                    <th>Status</th>
                    <th>Priority</th>
                    <th>Assigned To</th>
                    <th>Due Date</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($tasks as $task): ?>
                <tr>
                    <td>#<?php echo $task['id']; ?></td>
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
                    <td>
                        <?php if ($task['status'] !== 'completed'): ?>
                        <form method="POST" action="/tasks/<?php echo $task['id']; ?>/complete" style="display: inline;">
                            <input type="hidden" name="_token" value="<?php echo htmlspecialchars($csrfToken); ?>">
                            <button type="submit" class="btn btn-sm btn-primary">Complete</button>
                        </form>
                        <?php else: ?>
                        <span style="color: #888; font-size: 0.8rem;">Done</span>
                        <?php endif; ?>
                    </td>
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