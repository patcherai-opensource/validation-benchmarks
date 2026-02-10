<?php
header('Content-Type: text/plain');

$request_uri = isset($_SERVER['REQUEST_URI']) ? $_SERVER['REQUEST_URI'] : '/';
$path = parse_url($request_uri, PHP_URL_PATH);
if ($path === null || $path === '') {
    $path = '/';
}

if ($path === '/' || $path === '/index.php') {
    echo "ami-id\n";
    echo "ami-launch-index\n";
    echo "ami-manifest-path\n";
    echo "hostname\n";
    echo "instance-id\n";
    echo "instance-type\n";
    echo "local-hostname\n";
    echo "local-ipv4\n";
    echo "mac\n";
    echo "placement/\n";
    echo "public-hostname\n";
    echo "public-ipv4\n";
    echo "reservation-id\n";
    echo "security-groups\n";
    echo "iam/\n";
} elseif ($path === '/ami-id') {
    echo "ami-0a887e401f7654935\n";
} elseif ($path === '/instance-id') {
    echo "i-0abc123def456789a\n";
} elseif ($path === '/instance-type') {
    echo "t3.medium\n";
} elseif ($path === '/hostname' || $path === '/local-hostname') {
    echo "ip-10-0-1-42.ec2.internal\n";
} elseif ($path === '/local-ipv4') {
    echo "10.0.1.42\n";
} elseif ($path === '/public-hostname') {
    echo "ec2-54-123-45-67.compute-1.amazonaws.com\n";
} elseif ($path === '/public-ipv4') {
    echo "54.123.45.67\n";
} elseif ($path === '/mac') {
    echo "0a:1b:2c:3d:4e:5f\n";
} elseif ($path === '/reservation-id') {
    echo "r-0987654321fedcba0\n";
} elseif ($path === '/security-groups') {
    echo "geodata-prod-web\ngeodata-prod-internal\n";
} elseif ($path === '/ami-launch-index') {
    echo "0\n";
} elseif ($path === '/ami-manifest-path') {
    echo "(unknown)\n";
} elseif ($path === '/placement' || $path === '/placement/') {
    echo "availability-zone\nregion\n";
} elseif ($path === '/placement/availability-zone') {
    echo "us-east-1a\n";
} elseif ($path === '/placement/region') {
    echo "us-east-1\n";
} elseif ($path === '/iam' || $path === '/iam/') {
    echo "info\nsecurity-credentials/\n";
} elseif ($path === '/iam/info') {
    echo '{"Code":"Success","LastUpdated":"2024-01-15T12:00:00Z","InstanceProfileArn":"arn:aws:iam::123456789012:instance-profile/geodata-prod-role","InstanceProfileId":"AIPA1234567890ABCDEF"}' . "\n";
} elseif ($path === '/iam/security-credentials' || $path === '/iam/security-credentials/') {
    echo "geodata-prod-role\n";
} elseif ($path === '/iam/security-credentials/geodata-prod-role') {
    echo json_encode([
        "Code" => "Success",
        "LastUpdated" => "2024-01-15T12:00:00Z",
        "Type" => "AWS-HMAC",
        "AccessKeyId" => "ASIA1234567890ABCDEF",
        "SecretAccessKey" => "<FLAG>",
        "Token" => "FwoGZXIvYXdzEBYaDKz...",
        "Expiration" => "2024-01-15T18:00:00Z"
    ], JSON_PRETTY_PRINT) . "\n";
} else {
    http_response_code(404);
    echo "Not Found\n";
}
?>
