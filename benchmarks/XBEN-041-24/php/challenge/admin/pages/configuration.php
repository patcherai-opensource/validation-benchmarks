<?php
/**
 * Configuration page - Admin
 *
 * @package   myKnowledgeBase
 */
?>

<div class="admin-header">
    <h1>Configuration</h1>
</div>

<div class="card">
    <h2>General Settings</h2>
    <table class="table">
        <tbody>
            <?php foreach ($mkb_config as $key => $value): ?>
            <tr>
                <td style="width:40%;font-weight:500;"><?php echo htmlspecialchars($key); ?></td>
                <td><?php echo htmlspecialchars(is_bool($value) ? ($value ? 'true' : 'false') : (string)$value); ?></td>
            </tr>
            <?php endforeach; ?>
        </tbody>
    </table>
</div>

<div class="card">
    <h2>Available Languages</h2>
    <table class="table">
        <thead>
            <tr><th>Code</th><th>Language</th></tr>
        </thead>
        <tbody>
            <?php foreach ($mkb_languages as $code => $name): ?>
            <tr>
                <td><?php echo htmlspecialchars($code); ?></td>
                <td><?php echo htmlspecialchars($name); ?></td>
            </tr>
            <?php endforeach; ?>
        </tbody>
    </table>
</div>
