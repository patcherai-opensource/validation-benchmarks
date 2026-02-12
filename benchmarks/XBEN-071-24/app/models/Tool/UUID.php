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

namespace Pimcore\Model\Tool;

class UUID
{
    protected $uuid;
    protected $itemId;
    protected $type;
    protected $instanceIdentifier;

    /**
     * Get UUID record by its UUID value
     *
     * @param string $uuid
     * @return array|null
     */
    public static function getByUuid($uuid)
    {
        $dao = new UUID\Dao();
        return $dao->getByUuid($uuid);
    }

    /**
     * Check if UUID exists
     *
     * @param string $uuid
     * @return bool
     */
    public static function exists($uuid)
    {
        $dao = new UUID\Dao();
        return $dao->exists($uuid);
    }

    /**
     * Generate a new UUID v4
     *
     * @return string
     */
    public static function generateUuid()
    {
        return sprintf(
            '%04x%04x-%04x-%04x-%04x-%04x%04x%04x',
            mt_rand(0, 0xffff), mt_rand(0, 0xffff),
            mt_rand(0, 0xffff),
            mt_rand(0, 0x0fff) | 0x4000,
            mt_rand(0, 0x3fff) | 0x8000,
            mt_rand(0, 0xffff), mt_rand(0, 0xffff), mt_rand(0, 0xffff)
        );
    }

    // Getters and setters
    public function getUuid() { return $this->uuid; }
    public function setUuid($uuid) { $this->uuid = $uuid; return $this; }
    public function getItemId() { return $this->itemId; }
    public function setItemId($itemId) { $this->itemId = $itemId; return $this; }
    public function getType() { return $this->type; }
    public function setType($type) { $this->type = $type; return $this; }
    public function getInstanceIdentifier() { return $this->instanceIdentifier; }
    public function setInstanceIdentifier($id) { $this->instanceIdentifier = $id; return $this; }
}
