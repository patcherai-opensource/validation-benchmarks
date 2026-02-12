package com.assetportal.model;

public enum AssetCategory {
    HARDWARE("Hardware", "Physical computing equipment"),
    SOFTWARE("Software", "Licensed software applications"),
    NETWORK("Network", "Network infrastructure components"),
    PERIPHERAL("Peripheral", "Peripheral devices and accessories"),
    FURNITURE("Furniture", "Office furniture and fixtures");

    private final String displayName;
    private final String description;

    AssetCategory(String displayName, String description) {
        this.displayName = displayName;
        this.description = description;
    }

    public String getDisplayName() {
        return displayName;
    }

    public String getDescription() {
        return description;
    }
}
