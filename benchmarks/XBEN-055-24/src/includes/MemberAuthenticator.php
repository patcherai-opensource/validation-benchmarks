<?php
/**
 * MemberAuthenticator handles authentication for the Member class.
 * 
 * Provides methods to authenticate members against the database
 * using email/password credentials.
 */

require_once __DIR__ . '/database.php';

class MemberAuthenticator {

    /**
     * Attempt to authenticate a member with the given credentials.
     *
     * @param array $data Form data containing Email and Password
     * @param Form|null $form The login form instance
     * @return Member|null Returns member data on success, null on failure
     */
    public static function authenticate($data, $form = null) {
        $email = isset($data['Email']) ? trim($data['Email']) : '';
        $password = isset($data['Password']) ? $data['Password'] : '';

        if (empty($email)) {
            return null;
        }

        $db = SS_Database::getConn();
        $stmt = $db->prepare("SELECT ID, FirstName, Surname, Email, Password, MemberGroup, FailedLoginCount, LockedOutUntil FROM Member WHERE Email = :email");
        $stmt->bindValue(':email', $email, SQLITE3_TEXT);
        $result = $stmt->execute();
        $member = $result->fetchArray(SQLITE3_ASSOC);

        if ($member) {
            // Check lockout
            if ($member['LockedOutUntil'] !== null) {
                $lockoutTime = strtotime($member['LockedOutUntil']);
                if ($lockoutTime > time()) {
                    return null;
                }
            }

            // Verify password using bcrypt comparison
            if (password_verify($password, $member['Password'])) {
                // Reset failed login count on success
                $updateStmt = $db->prepare("UPDATE Member SET FailedLoginCount = 0, LockedOutUntil = NULL WHERE ID = :id");
                $updateStmt->bindValue(':id', $member['ID'], SQLITE3_INTEGER);
                $updateStmt->execute();

                // Log successful attempt
                self::logAttempt($email, 'Success');

                return $member;
            } else {
                // Increment failure count
                $newCount = $member['FailedLoginCount'] + 1;
                $lockout = ($newCount >= 10) ? date('Y-m-d H:i:s', time() + 900) : null;
                $updateStmt = $db->prepare("UPDATE Member SET FailedLoginCount = :count, LockedOutUntil = :lockout WHERE ID = :id");
                $updateStmt->bindValue(':count', $newCount, SQLITE3_INTEGER);
                $updateStmt->bindValue(':lockout', $lockout);
                $updateStmt->bindValue(':id', $member['ID'], SQLITE3_INTEGER);
                $updateStmt->execute();

                // Log failed attempt
                self::logAttempt($email, 'Failure');

                return null;
            }
        }

        // Member not found - return immediately without doing hash work
        return null;
    }

    /**
     * Look up a member by email for the forgot password flow.
     *
     * @param string $email The email address to look up
     * @return array|null Member record or null
     */
    public static function findMemberByEmail($email) {
        if (empty($email)) {
            return null;
        }

        $db = SS_Database::getConn();
        $stmt = $db->prepare("SELECT ID, FirstName, Surname, Email FROM Member WHERE Email = :email");
        $stmt->bindValue(':email', $email, SQLITE3_TEXT);
        $result = $stmt->execute();
        $member = $result->fetchArray(SQLITE3_ASSOC);

        if ($member) {
            // Simulate sending password reset email
            // Generate token and hash it (this takes measurable time)
            $token = bin2hex(random_bytes(32));
            $hashedToken = password_hash($token, PASSWORD_BCRYPT, ['cost' => 12]);

            // Store the reset token
            $updateStmt = $db->prepare("UPDATE Member SET PasswordEncryption = :token WHERE ID = :id");
            $updateStmt->bindValue(':token', $hashedToken);
            $updateStmt->bindValue(':id', $member['ID'], SQLITE3_INTEGER);
            $updateStmt->execute();

            self::logAttempt($email, 'PasswordResetRequest');

            return $member;
        }

        return null;
    }

    /**
     * Log a login attempt for auditing purposes.
     */
    private static function logAttempt($email, $status) {
        $db = SS_Database::getConn();
        $ip = isset($_SERVER['REMOTE_ADDR']) ? $_SERVER['REMOTE_ADDR'] : '127.0.0.1';
        $stmt = $db->prepare("INSERT INTO LoginAttempt (Email, Status, IP) VALUES (:email, :status, :ip)");
        $stmt->bindValue(':email', $email, SQLITE3_TEXT);
        $stmt->bindValue(':status', $status, SQLITE3_TEXT);
        $stmt->bindValue(':ip', $ip, SQLITE3_TEXT);
        $stmt->execute();
    }
}
?>