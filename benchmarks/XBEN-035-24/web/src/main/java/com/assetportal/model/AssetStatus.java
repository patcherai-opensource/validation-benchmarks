package com.assetportal.model;

public enum AssetStatus {
    ACTIVE("Active"),
    MAINTENANCE("Under Maintenance"),
    DECOMMISSIONED("Decommissioned"),
    RESERVED("Reserved");

    private final String label;

    AssetStatus(String label) {
        this.label = label;
    }

    public String getLabel() {
        return label;
    }
}
