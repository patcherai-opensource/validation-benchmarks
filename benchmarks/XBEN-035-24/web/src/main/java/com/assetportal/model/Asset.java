package com.assetportal.model;

import java.util.Date;

public class Asset {

    private int id;
    private String name;
    private String serialNumber;
    private AssetCategory category;
    private AssetStatus status;
    private Location location;
    private String assignedTo;
    private Date purchaseDate;
    private double purchasePrice;
    private String notes;

    public Asset() {}

    public Asset(int id, String name, String serialNumber, AssetCategory category,
                 AssetStatus status, Location location, String assignedTo,
                 Date purchaseDate, double purchasePrice, String notes) {
        this.id = id;
        this.name = name;
        this.serialNumber = serialNumber;
        this.category = category;
        this.status = status;
        this.location = location;
        this.assignedTo = assignedTo;
        this.purchaseDate = purchaseDate;
        this.purchasePrice = purchasePrice;
        this.notes = notes;
    }

    public int getId() { return id; }
    public void setId(int id) { this.id = id; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getSerialNumber() { return serialNumber; }
    public void setSerialNumber(String serialNumber) { this.serialNumber = serialNumber; }

    public AssetCategory getCategory() { return category; }
    public void setCategory(AssetCategory category) { this.category = category; }

    public AssetStatus getStatus() { return status; }
    public void setStatus(AssetStatus status) { this.status = status; }

    public Location getLocation() { return location; }
    public void setLocation(Location location) { this.location = location; }

    public String getAssignedTo() { return assignedTo; }
    public void setAssignedTo(String assignedTo) { this.assignedTo = assignedTo; }

    public Date getPurchaseDate() { return purchaseDate; }
    public void setPurchaseDate(Date purchaseDate) { this.purchaseDate = purchaseDate; }

    public double getPurchasePrice() { return purchasePrice; }
    public void setPurchasePrice(double purchasePrice) { this.purchasePrice = purchasePrice; }

    public String getNotes() { return notes; }
    public void setNotes(String notes) { this.notes = notes; }
}
