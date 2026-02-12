package com.assetportal.model;

public class Location {

    private String building;
    private String floor;
    private String room;

    public Location() {}

    public Location(String building, String floor, String room) {
        this.building = building;
        this.floor = floor;
        this.room = room;
    }

    public String getBuilding() {
        return building;
    }

    public void setBuilding(String building) {
        this.building = building;
    }

    public String getFloor() {
        return floor;
    }

    public void setFloor(String floor) {
        this.floor = floor;
    }

    public String getRoom() {
        return room;
    }

    public void setRoom(String room) {
        this.room = room;
    }

    @Override
    public String toString() {
        return building + ", Floor " + floor + ", Room " + room;
    }
}
