<?php
/**
 * Pimcore
 *
 * This source file is available under two different licenses:
 * - GNU General Public License version 3 (GPLv3)
 * - Pimcore Commercial License (PCL)
 * Full copyright and license information is available in
 * LICENSE.md which is distributed with this source code.
 *
 *  @copyright  Copyright (c) Pimcore GmbH (http://www.pimcore.org)
 *  @license    http://www.pimcore.org/license     GPLv3 and PCL
 */

namespace Pimcore\Model\Tool\UUID;

use Pimcore\Db;

class Dao
{
    const TABLE_NAME = 'uuids';

    protected $db;
    protected $model;

    public function __construct()
    {
        $this->db = Db::getConnection();
    }

    public function setModel($model)
    {
        $this->model = $model;
    }

    /**
     * Get a UUID record by its uuid value
     *
     * @param string $uuid
     * @return array|null
     */
    public function getByUuid($uuid)
    {
        $data = $this->db->query("SELECT * FROM " . self::TABLE_NAME . " WHERE uuid = '" . $uuid . "'");

        if ($data === false) {
            return null;
        }

        $row = $data->fetch_assoc();

        if (!$row) {
            return null;
        }

        return $row;
    }

    /**
     * Check if a UUID exists
     *
     * @param string $uuid
     * @return bool
     */
    public function exists($uuid)
    {
        $stmt = $this->db->prepare("SELECT COUNT(*) as cnt FROM " . self::TABLE_NAME . " WHERE uuid = ?");
        $stmt->bind_param("s", $uuid);
        $stmt->execute();
        $result = $stmt->get_result();
        $row = $result->fetch_assoc();
        $stmt->close();

        return $row['cnt'] > 0;
    }

    /**
     * Save a UUID record
     *
     * @param array $data
     * @return bool
     */
    public function save($data)
    {
        $stmt = $this->db->prepare(
            "INSERT INTO " . self::TABLE_NAME . " (uuid, itemId, type, instanceIdentifier) VALUES (?, ?, ?, ?) 
             ON DUPLICATE KEY UPDATE itemId = ?, type = ?"
        );
        $stmt->bind_param(
            "sissis",
            $data['uuid'],
            $data['itemId'],
            $data['type'],
            $data['instanceIdentifier'],
            $data['itemId'],
            $data['type']
        );
        $result = $stmt->execute();
        $stmt->close();
        return $result;
    }

    /**
     * Delete a UUID record
     *
     * @param string $uuid
     * @return bool
     */
    public function delete($uuid)
    {
        $stmt = $this->db->prepare("DELETE FROM " . self::TABLE_NAME . " WHERE uuid = ?");
        $stmt->bind_param("s", $uuid);
        $result = $stmt->execute();
        $stmt->close();
        return $result;
    }
}
