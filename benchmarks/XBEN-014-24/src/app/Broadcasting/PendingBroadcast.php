<?php

namespace App\Broadcasting;

class PendingBroadcast
{
    protected $events;
    protected $event;

    public function __construct($events, $event)
    {
        $this->event = $event;
        $this->events = $events;
    }

    public function __destruct()
    {
        $this->events->dispatch($this->event);
    }
}