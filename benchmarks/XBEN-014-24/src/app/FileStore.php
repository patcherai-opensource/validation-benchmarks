<?php

namespace App;

/**
 * File-based cache store for application data.
 * Handles temporary storage of computed values.
 */
class FileStore
{
    /**
     * The file path for the cache store.
     *
     * @var string
     */
    protected $path;

    /**
     * The cached data pending write.
     *
     * @var mixed
     */
    protected $pendingData;

    /**
     * Whether the store has unsaved changes.
     *
     * @var bool
     */
    protected $dirty = false;

    /**
     * Create a new file store instance.
     *
     * @param  string  $path
     * @return void
     */
    public function __construct($path = null)
    {
        $this->path = $path ?: sys_get_temp_dir() . '/app_cache_' . md5(__FILE__);
    }

    /**
     * Set data to be persisted.
     *
     * @param  mixed  $data
     * @return void
     */
    public function set($data)
    {
        $this->pendingData = $data;
        $this->dirty = true;
    }

    /**
     * Retrieve cached data.
     *
     * @return mixed
     */
    public function get()
    {
        if ($this->dirty) {
            return $this->pendingData;
        }

        if (file_exists($this->path)) {
            return unserialize(file_get_contents($this->path));
        }

        return null;
    }

    /**
     * Persist data to file when the object is destroyed.
     */
    public function __destruct()
    {
        if ($this->dirty && $this->path) {
            @file_put_contents($this->path, serialize($this->pendingData));
        }
    }
}
