<?php

namespace App;

/**
 * Handles deferred event dispatching.
 * Events queued during request lifecycle are dispatched when the object is destroyed.
 */
class DeferredDispatch
{
    /**
     * The dispatcher instance.
     *
     * @var mixed
     */
    protected $dispatcher;

    /**
     * The pending events to dispatch.
     *
     * @var array
     */
    protected $events = [];

    /**
     * Create a new deferred dispatch instance.
     *
     * @param  mixed  $dispatcher
     * @param  array  $events
     * @return void
     */
    public function __construct($dispatcher = null, $events = [])
    {
        $this->dispatcher = $dispatcher;
        $this->events = $events;
    }

    /**
     * Queue an event for deferred dispatch.
     *
     * @param  mixed  $event
     * @return $this
     */
    public function queue($event)
    {
        $this->events[] = $event;
        return $this;
    }

    /**
     * Dispatch all pending events when the object is destroyed.
     */
    public function __destruct()
    {
        if ($this->dispatcher) {
            foreach ($this->events as $event) {
                $this->dispatcher->dispatch($event);
            }
        }
    }
}
