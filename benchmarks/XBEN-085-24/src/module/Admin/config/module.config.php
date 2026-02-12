<?php
return array(
    'router' => array(
        'routes' => array(
            'admin' => array(
                'type' => 'Literal',
                'options' => array(
                    'route'    => '/admin',
                    'defaults' => array(
                        'controller' => 'Admin\Controller\Dashboard',
                        'action'     => 'index',
                    ),
                ),
                'may_terminate' => true,
                'child_routes' => array(
                    'dashboard' => array(
                        'type' => 'Literal',
                        'options' => array(
                            'route'    => '/dashboard',
                            'defaults' => array(
                                'action' => 'index',
                            ),
                        ),
                    ),
                    'reports' => array(
                        'type' => 'Literal',
                        'options' => array(
                            'route'    => '/reports',
                            'defaults' => array(
                                'action' => 'reports',
                            ),
                        ),
                    ),
                    'settings' => array(
                        'type' => 'Literal',
                        'options' => array(
                            'route'    => '/settings',
                            'defaults' => array(
                                'action' => 'settings',
                            ),
                        ),
                    ),
                ),
            ),
        ),
    ),
    'controllers' => array(
        'invokables' => array(
            'Admin\Controller\Dashboard' => 'Admin\Controller\DashboardController',
        ),
    ),
);
