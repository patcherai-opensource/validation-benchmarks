<?php

namespace App;

/**
 * Command dispatcher for processing queued commands.
 * Supports various dispatch strategies.
 */
class CommandDispatcher
{
    /**
     * The command processing callback.
     *
     * @var callable|null
     */
    protected $handler;

    /**
     * Create a new command dispatcher instance.
     *
     * @param  callable|null  $handler
     * @return void
     */
    public function __construct($handler = null)
    {
        $this->handler = $handler;
    }

    /**
     * Dispatch a command for execution.
     *
     * @param  mixed  $command
     * @return mixed
     */
    public function dispatch($command)
    {
        if (is_callable($this->handler)) {
            return call_user_func($this->handler, $command);
        }

        return null;
    }
}
