<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <meta name="csrf-token" content="<?php echo htmlspecialchars($csrf_token); ?>">
    <title>RaspAP WiFi Configuration Portal</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
    <link rel="stylesheet" href="/css/custom.css">
</head>
<body id="page-top">
    <div id="wrapper">
        <!-- Sidebar -->
        <ul class="navbar-nav bg-gradient-primary sidebar sidebar-dark accordion" id="accordionSidebar">
            <a class="sidebar-brand d-flex align-items-center justify-content-center" href="/">
                <div class="sidebar-brand-icon">
                    <i class="fas fa-wifi"></i>
                </div>
                <div class="sidebar-brand-text mx-3">RaspAP</div>
            </a>
            <hr class="sidebar-divider my-0">
            <li class="nav-item <?php echo $page === 'dashboard' ? 'active' : ''; ?>">
                <a class="nav-link" href="/?page=dashboard"><i class="fas fa-tachometer-alt"></i> <span>Dashboard</span></a>
            </li>
            <hr class="sidebar-divider">
            <div class="sidebar-heading">Interfaces</div>
            <li class="nav-item <?php echo $page === 'wlan0_info' ? 'active' : ''; ?>">
                <a class="nav-link" href="/?page=wlan0_info"><i class="fas fa-network-wired"></i> <span>WiFi client</span></a>
            </li>
            <li class="nav-item <?php echo $page === 'hostapd_conf' ? 'active' : ''; ?>">
                <a class="nav-link" href="/?page=hostapd_conf"><i class="fas fa-broadcast-tower"></i> <span>Hotspot</span></a>
            </li>
            <hr class="sidebar-divider">
            <div class="sidebar-heading">VPN</div>
            <li class="nav-item <?php echo $page === 'wg_conf' ? 'active' : ''; ?>">
                <a class="nav-link" href="/?page=wg_conf"><i class="fas fa-key"></i> <span>WireGuard</span></a>
            </li>
            <li class="nav-item <?php echo $page === 'openvpn_conf' ? 'active' : ''; ?>">
                <a class="nav-link" href="/?page=openvpn_conf"><i class="fas fa-shield-alt"></i> <span>OpenVPN</span></a>
            </li>
            <hr class="sidebar-divider">
            <div class="sidebar-heading">System</div>
            <li class="nav-item <?php echo $page === 'system_info' ? 'active' : ''; ?>">
                <a class="nav-link" href="/?page=system_info"><i class="fas fa-info-circle"></i> <span>System</span></a>
            </li>
            <li class="nav-item <?php echo $page === 'about' ? 'active' : ''; ?>">
                <a class="nav-link" href="/?page=about"><i class="fas fa-question-circle"></i> <span>About</span></a>
            </li>
            <hr class="sidebar-divider d-none d-md-block">
        </ul>
        <!-- End Sidebar -->

        <div id="content-wrapper" class="d-flex flex-column">
            <div id="content">
                <!-- Topbar -->
                <nav class="navbar navbar-expand navbar-light bg-white topbar mb-4 static-top shadow">
                    <span class="mr-2 d-none d-lg-inline text-gray-600 small">RaspAP v<?php echo RASPI_VERSION; ?></span>
                    <ul class="navbar-nav ml-auto">
                        <li class="nav-item">
                            <a class="nav-link" href="/?page=auth&logout=1">
                                <i class="fas fa-sign-out-alt fa-sm fa-fw mr-2 text-gray-400"></i> Logout
                            </a>
                        </li>
                    </ul>
                </nav>
                <!-- End Topbar -->

                <div class="container-fluid">
