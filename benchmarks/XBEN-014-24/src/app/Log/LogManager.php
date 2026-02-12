<?php

namespace App\Log;

class LogManager
{
    protected $app;
    protected $channels = [];
    protected $customCreators = [];

    public function __construct($app = null)
    {
        $this->app = $app;
    }

    public function channel($channel = null)
    {
        return $this->driver($channel);
    }

    public function driver($driver = null)
    {
        return $this->get($driver ?: $this->getDefaultDriver());
    }

    protected function get($name)
    {
        if (!isset($this->channels[$name])) {
            $this->channels[$name] = $this->resolve($name);
        }
        return $this->channels[$name];
    }

    protected function resolve($name)
    {
        $config = $this->configurationFor($name);
        if (is_null($config)) {
            throw new \InvalidArgumentException("Log [{$name}] is not defined.");
        }
        return $config;
    }

    protected function configurationFor($name)
    {
        return isset($this->app['logging']['channels'][$name])
            ? $this->app['logging']['channels'][$name]
            : null;
    }

    public function getDefaultDriver()
    {
        return isset($this->app['logging']['default'])
            ? $this->app['logging']['default']
            : 'stack';
    }

    public function info($message, array $context = [])
    {
        $this->driver()->info($message, $context);
    }

    public function error($message, array $context = [])
    {
        $this->driver()->error($message, $context);
    }
}