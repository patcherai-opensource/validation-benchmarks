<?php

namespace App\Bus;

class Dispatcher
{
    protected $queueResolver;

    public function __construct($queueResolver = null)
    {
        $this->queueResolver = $queueResolver;
    }

    public function dispatch($command)
    {
        if (is_callable($this->queueResolver)) {
            return call_user_func($this->queueResolver, $command);
        }
        return $this->dispatchNow($command);
    }

    public function dispatchNow($command)
    {
        return $command;
    }
}