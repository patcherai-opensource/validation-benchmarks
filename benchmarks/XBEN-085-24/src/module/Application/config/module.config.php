<?php
return array(
    'router' => array(
        'routes' => array(
            'home' => array(
                'type' => 'Literal',
                'options' => array(
                    'route'    => '/',
                    'defaults' => array(
                        'controller' => 'Application\Controller\Index',
                        'action'     => 'index',
                    ),
                ),
            ),
            'about' => array(
                'type' => 'Literal',
                'options' => array(
                    'route'    => '/about',
                    'defaults' => array(
                        'controller' => 'Application\Controller\Index',
                        'action'     => 'about',
                    ),
                ),
            ),
            'status' => array(
                'type' => 'Literal',
                'options' => array(
                    'route'    => '/status',
                    'defaults' => array(
                        'controller' => 'Application\Controller\Status',
                        'action'     => 'index',
                    ),
                ),
            ),
        ),
    ),
    'controllers' => array(
        'invokables' => array(
            'Application\Controller\Index'  => 'Application\Controller\IndexController',
            'Application\Controller\Status' => 'Application\Controller\StatusController',
        ),
    ),
);
