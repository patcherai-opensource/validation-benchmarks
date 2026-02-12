<?php

namespace App\Cache;

class CacheManager
{
    protected $app;
    protected $stores = [];
    protected $customCreators = [];

    public function __construct($app = null)
    {
        $this->app = $app;
    }

    public function store($name = null)
    {
        $name = $name ?: $this->getDefaultDriver();

        return $this->stores[$name] = $this->getStore($name);
    }

    protected function getStore($name)
    {
        return isset($this->stores[$name]) ? $this->stores[$name] : $this->resolve($name);
    }

    protected function resolve($name)
    {
        $config = $this->getConfig($name);

        if (is_null($config)) {
            throw new \InvalidArgumentException("Cache store [{$name}] is not defined.");
        }

        $driverMethod = 'create' . ucfirst($config['driver']) . 'Driver';

        if (method_exists($this, $driverMethod)) {
            return $this->{$driverMethod}($config);
        }

        throw new \InvalidArgumentException("Driver [{$config['driver']}] is not supported.");
    }

    protected function getConfig($name)
    {
        return isset($this->app['cache']['stores'][$name])
            ? $this->app['cache']['stores'][$name]
            : null;
    }

    public function getDefaultDriver()
    {
        return isset($this->app['cache']['default'])
            ? $this->app['cache']['default']
            : 'file';
    }

    public function put($key, $value, $ttl = null)
    {
        return $this->store()->put($key, $value, $ttl);
    }

    public function get($key, $default = null)
    {
        return $this->store()->get($key, $default);
    }

    public function forget($key)
    {
        return $this->store()->forget($key);
    }
}
