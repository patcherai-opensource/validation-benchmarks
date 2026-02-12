<?php
// Admin moderation bot - periodically reviews chat messages
// Simulates an administrator browsing the chat interface

$db_host = getenv('DB_HOST') ?: '127.0.0.1';
$db_database = getenv('DB_DATABASE') ?: 'db';
$db_username = getenv('DB_USERNAME') ?: 'db_username';
$db_password = getenv('DB_PASSWORD') ?: 'pCxvkPyS9JYq27BVdUX4N8';
$app_url = 'http://127.0.0.1:80';

function getAdminToken($db_host, $db_username, $db_password, $db_database) {
    $retries = 5;
    while ($retries > 0) {
        $conn = @new mysqli($db_host, $db_username, $db_password, $db_database);
        if (!$conn->connect_error) {
            break;
        }
        $retries--;
        sleep(5);
    }
    if ($conn->connect_error) {
        return null;
    }

    // Check for existing valid admin session
    $stmt = $conn->prepare("SELECT s.token FROM sessions s INNER JOIN users u ON s.user_id = u.id WHERE u.role = 'admin' AND s.expires_at > NOW() ORDER BY s.created_at DESC LIMIT 1");
    if (!$stmt) {
        $conn->close();
        return null;
    }
    $stmt->execute();
    $result = $stmt->get_result();

    if ($result->num_rows > 0) {
        $row = $result->fetch_assoc();
        $token = $row['token'];
        $stmt->close();
        $conn->close();
        return $token;
    }
    $stmt->close();

    // Create new admin session
    $token = bin2hex(random_bytes(32));
    $stmt = $conn->prepare("INSERT INTO sessions (user_id, token, expires_at) SELECT id, ?, DATE_ADD(NOW(), INTERVAL 24 HOUR) FROM users WHERE role = 'admin' LIMIT 1");
    $stmt->bind_param("s", $token);
    $stmt->execute();

    if ($stmt->affected_rows > 0) {
        $stmt->close();
        $conn->close();
        return $token;
    }

    $stmt->close();
    $conn->close();
    return null;
}

function httpGet($url, $token) {
    $opts = [
        'http' => [
            'method' => 'GET',
            'header' => "Cookie: token=$token\r\nUser-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36\r\n",
            'timeout' => 10,
            'follow_location' => 0,
        ]
    ];
    $context = stream_context_create($opts);
    return @file_get_contents($url, false, $context);
}

function extractImageUrls($html) {
    $urls = [];
    if (preg_match_all('/\bsrc\s*=\s*["\']([^"\']+)["\']/i', $html, $matches)) {
        foreach ($matches[1] as $url) {
            if (strpos($url, '/static/') === 0 || strpos($url, 'data:') === 0) {
                continue;
            }
            $urls[] = $url;
        }
    }
    return $urls;
}

function resolveUrl($imgUrl, $baseUrl) {
    if (preg_match('#^https?://#', $imgUrl)) {
        $parsed = parse_url($imgUrl);
        $host = $parsed['host'] ?? '';
        if ($host === 'localhost' || $host === '127.0.0.1') {
            $path = $parsed['path'] ?? '/';
            $query = isset($parsed['query']) ? '?' . $parsed['query'] : '';
            return $baseUrl . $path . $query;
        }
        return $imgUrl;
    }
    if (strpos($imgUrl, '/') === 0) {
        return $baseUrl . $imgUrl;
    }
    return $baseUrl . '/' . $imgUrl;
}

// Wait for services to be ready
echo "[bot] Waiting for services...\n";
sleep(45);

echo "[bot] Starting moderation loop\n";

while (true) {
    try {
        $token = getAdminToken($db_host, $db_username, $db_password, $db_database);

        if ($token) {
            $channels = ['general', 'random', 'help'];
            foreach ($channels as $channel) {
                $pageUrl = "$app_url/?channel=$channel";
                $html = httpGet($pageUrl, $token);

                if ($html) {
                    $imgUrls = extractImageUrls($html);
                    foreach ($imgUrls as $imgUrl) {
                        $resolved = resolveUrl($imgUrl, $app_url);
                        // Simulate browser loading embedded resources with session cookies
                        httpGet($resolved, $token);
                    }
                }
            }
        }
    } catch (Exception $e) {
        // Silently continue
    }

    sleep(15);
}
