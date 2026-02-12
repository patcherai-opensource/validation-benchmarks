package com.assetportal.util;

import com.assetportal.model.*;

import java.util.*;

public class AssetRepository {

    private static final Map<Integer, Asset> assets = new LinkedHashMap<>();

    static {
        assets.put(1, new Asset(1, "Dell OptiPlex 7090", "SN-DL-7090-0142",
                AssetCategory.HARDWARE, AssetStatus.ACTIVE,
                new Location("HQ-Building A", "3", "301"),
                "jsmith@corp.local", new Date(1640995200000L), 1249.99, "Workstation for engineering team"));

        assets.put(2, new Asset(2, "Cisco Catalyst 9300", "SN-CS-9300-0087",
                AssetCategory.NETWORK, AssetStatus.ACTIVE,
                new Location("DC-East", "1", "Server Room B"),
                "netops@corp.local", new Date(1625097600000L), 4899.00, "Core switch for east datacenter"));

        assets.put(3, new Asset(3, "Adobe Creative Suite", "LIC-ADB-CS-2024-155",
                AssetCategory.SOFTWARE, AssetStatus.ACTIVE,
                new Location("HQ-Building A", "2", "205"),
                "mdesign@corp.local", new Date(1672531200000L), 599.99, "Annual license - design department"));

        assets.put(4, new Asset(4, "HP LaserJet Pro M454", "SN-HP-M454-0033",
                AssetCategory.PERIPHERAL, AssetStatus.MAINTENANCE,
                new Location("HQ-Building B", "1", "Print Room"),
                "facilities@corp.local", new Date(1609459200000L), 449.00, "Color printer - needs toner replacement"));

        assets.put(5, new Asset(5, "Standing Desk - ErgoTech", "FRN-ET-SD-0221",
                AssetCategory.FURNITURE, AssetStatus.ACTIVE,
                new Location("HQ-Building A", "4", "402"),
                "alee@corp.local", new Date(1656633600000L), 799.00, "Electric sit-stand desk"));

        assets.put(6, new Asset(6, "ThinkPad X1 Carbon Gen 10", "SN-LN-X1C-0198",
                AssetCategory.HARDWARE, AssetStatus.RESERVED,
                new Location("HQ-Building A", "1", "IT Storage"),
                "it-provisioning@corp.local", new Date(1680307200000L), 1899.99, "Reserved for new hire starting 2024-03"));

        assets.put(7, new Asset(7, "Palo Alto PA-440", "SN-PA-440-0012",
                AssetCategory.NETWORK, AssetStatus.ACTIVE,
                new Location("DC-West", "1", "Network Closet A"),
                "secops@corp.local", new Date(1617235200000L), 2999.00, "Branch office firewall"));

        assets.put(8, new Asset(8, "Microsoft 365 E5", "LIC-MS-365E5-BULK",
                AssetCategory.SOFTWARE, AssetStatus.ACTIVE,
                new Location("Cloud", "-", "-"),
                "it-admin@corp.local", new Date(1664582400000L), 57.00, "Per-user monthly subscription - 250 seats"));

        assets.put(9, new Asset(9, "Logitech Rally Camera", "SN-LG-RALLY-0045",
                AssetCategory.PERIPHERAL, AssetStatus.DECOMMISSIONED,
                new Location("HQ-Building B", "2", "Conf Room C"),
                "facilities@corp.local", new Date(1577836800000L), 1299.00, "Replaced with newer model"));

        assets.put(10, new Asset(10, "Dell PowerEdge R750", "SN-DL-R750-0005",
                AssetCategory.HARDWARE, AssetStatus.ACTIVE,
                new Location("DC-East", "1", "Rack 12"),
                "sysadmin@corp.local", new Date(1688169600000L), 8499.00, "Application server - production cluster"));
    }

    public static Asset getById(int id) {
        return assets.get(id);
    }

    public static Collection<Asset> getAll() {
        return assets.values();
    }

    public static int count() {
        return assets.size();
    }
}
