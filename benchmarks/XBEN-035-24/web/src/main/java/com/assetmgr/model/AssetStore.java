package com.assetmgr.model;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Collection;

public class AssetStore {
    private static final AssetStore INSTANCE = new AssetStore();
    private final Map<String, Asset> assets = new LinkedHashMap<>();

    private AssetStore() {
        initializeSampleData();
    }

    public static AssetStore getInstance() {
        return INSTANCE;
    }

    private void initializeSampleData() {
        assets.put("AST-001", new Asset("AST-001", "Primary Database Server",
                "PostgreSQL production cluster node", AssetStatus.ACTIVE, Priority.CRITICAL,
                "DC-East-Rack12", "infrastructure@corp.local"));
        assets.put("AST-002", new Asset("AST-002", "Staging Web Server",
                "Nginx reverse proxy for staging environment", AssetStatus.ACTIVE, Priority.MEDIUM,
                "DC-West-Rack04", "webops@corp.local"));
        assets.put("AST-003", new Asset("AST-003", "Legacy Auth Service",
                "LDAP authentication gateway - pending migration", AssetStatus.MAINTENANCE, Priority.HIGH,
                "DC-East-Rack07", "security@corp.local"));
        assets.put("AST-004", new Asset("AST-004", "Monitoring Collector",
                "Prometheus metrics aggregator", AssetStatus.ACTIVE, Priority.LOW,
                "DC-West-Rack01", "monitoring@corp.local"));
        assets.put("AST-005", new Asset("AST-005", "Build Agent Pool",
                "Jenkins build agent - decommission scheduled", AssetStatus.DECOMMISSIONED, Priority.LOW,
                "DC-East-Rack15", "devops@corp.local"));
    }

    public Asset getAsset(String id) {
        return assets.get(id);
    }

    public Collection<Asset> getAllAssets() {
        return assets.values();
    }

    public void updateAsset(String id, Asset asset) {
        assets.put(id, asset);
    }

    public boolean hasAsset(String id) {
        return assets.containsKey(id);
    }
}
