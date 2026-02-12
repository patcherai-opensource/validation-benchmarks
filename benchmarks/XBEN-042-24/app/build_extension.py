#!/usr/bin/env python3
"""
Build script for the GData extension JAR package.
Packages the extension source and compiled classes into a distributable JAR.
"""
import os
import zipfile
import base64

# These credentials are used for internal service-to-service API auth
# In production, these should be set via system properties:
#   -Dext.gdata.clientid=...
#   -Dext.gdata.clientsecret=...
CLIENT_ID = "data-refinery-internal-svc"
CLIENT_SECRET = "xK9mP2vL7nQ4wR8jT1sY6bA3cF5hD0eG"

CLIENT_ID_B64 = base64.b64encode(CLIENT_ID.encode()).decode()
CLIENT_SECRET_B64 = base64.b64encode(CLIENT_SECRET.encode()).decode()

JAVA_SOURCE = f'''package com.google.refine.extension.gdata;

import java.util.Base64;

/**
 * Extension for Google Sheets / Google Drive integration.
 * Handles OAuth2 authentication flow and API access.
 */
public class GoogleAPIExtension {{

    private static final String CLIENT_ID = System.getProperty(
        "ext.gdata.clientid",
        new String(Base64.getDecoder().decode("{CLIENT_ID_B64}"))
    );

    private static final String CLIENT_SECRET = System.getProperty(
        "ext.gdata.clientsecret",
        new String(Base64.getDecoder().decode("{CLIENT_SECRET_B64}"))
    );

    private static final String REDIRECT_URI = "http://127.0.0.1:3333/command/gdata/authorize";
    private static final String SCOPE = "https://www.googleapis.com/auth/drive https://spreadsheets.google.com/feeds";

    public static String getAuthorizationUrl() {{
        return "https://accounts.google.com/o/oauth2/v2/auth"
            + "?client_id=" + CLIENT_ID
            + "&redirect_uri=" + REDIRECT_URI
            + "&response_type=code"
            + "&scope=" + SCOPE
            + "&access_type=offline";
    }}

    public static String getClientId() {{
        return CLIENT_ID;
    }}

    public static String getClientSecret() {{
        return CLIENT_SECRET;
    }}

    public static boolean isConfigured() {{
        return CLIENT_ID != null && !CLIENT_ID.isEmpty()
            && CLIENT_SECRET != null && !CLIENT_SECRET.isEmpty();
    }}
}}
'''

MANIFEST = """Manifest-Version: 1.0
Created-By: OpenRefine Build System
Extension-Name: gdata
Extension-Version: 1.4.0
Implementation-Title: OpenRefine GData Extension
Implementation-Version: 1.4.0
"""

MODULE_INFO = """<?xml version="1.0" encoding="UTF-8"?>
<module>
    <name>GData Extension</name>
    <description>Google Sheets and Google Drive integration</description>
    <version>1.4.0</version>
    <author>OpenRefine Contributors</author>
    <requires>
        <module>core</module>
    </requires>
</module>
"""

CONTROLLER_JS = """var html = "text/html";
var encoding = "UTF-8";

function init() {
    var RS = Packages.com.google.refine.RefineServlet;
    RS.registerCommand(module, "authorize", new Packages.com.google.refine.extension.gdata.AuthorizeCommand());
    RS.registerCommand(module, "deauthorize", new Packages.com.google.refine.extension.gdata.DeAuthorizeCommand());
    RS.registerCommand(module, "upload", new Packages.com.google.refine.extension.gdata.UploadCommand());
}
"""


def build_jar(output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as jar:
        # META-INF
        jar.writestr("META-INF/MANIFEST.MF", MANIFEST)
        
        # Java source file (included in JAR for reference, as OpenRefine did)
        jar.writestr(
            "com/google/refine/extension/gdata/GoogleAPIExtension.java",
            JAVA_SOURCE
        )
        
        # Additional source stubs to look realistic
        jar.writestr(
            "com/google/refine/extension/gdata/AuthorizeCommand.java",
            '''package com.google.refine.extension.gdata;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

public class AuthorizeCommand {
    public void doGet(HttpServletRequest request, HttpServletResponse response) {
        String authUrl = GoogleAPIExtension.getAuthorizationUrl();
        try {
            response.sendRedirect(authUrl);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
'''
        )
        
        jar.writestr(
            "com/google/refine/extension/gdata/DeAuthorizeCommand.java",
            '''package com.google.refine.extension.gdata;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

public class DeAuthorizeCommand {
    public void doGet(HttpServletRequest request, HttpServletResponse response) {
        try {
            request.getSession().removeAttribute("gdata_credentials");
            response.sendRedirect("/");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
'''
        )
        
        jar.writestr(
            "com/google/refine/extension/gdata/UploadCommand.java",
            '''package com.google.refine.extension.gdata;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

public class UploadCommand {
    public void doPost(HttpServletRequest request, HttpServletResponse response) {
        // Upload project data to Google Drive
        if (!GoogleAPIExtension.isConfigured()) {
            throw new RuntimeException("GData extension not configured");
        }
        // Implementation omitted
    }
}
'''
        )
        
        jar.writestr(
            "com/google/refine/extension/gdata/GDataImporter.java",
            '''package com.google.refine.extension.gdata;

import java.io.InputStream;
import java.net.URL;
import java.net.HttpURLConnection;

public class GDataImporter {
    
    public static InputStream importFromGoogleSheets(String spreadsheetId) throws Exception {
        String apiUrl = "https://sheets.googleapis.com/v4/spreadsheets/" + spreadsheetId + "/values/Sheet1";
        URL url = new URL(apiUrl);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("GET");
        conn.setRequestProperty("Authorization", "Bearer " + getAccessToken());
        return conn.getInputStream();
    }
    
    private static String getAccessToken() {
        // Retrieve from session or refresh using client credentials
        return "";
    }
}
'''
        )
        
        # Module config
        jar.writestr("module/module.xml", MODULE_INFO)
        jar.writestr("module/controller.js", CONTROLLER_JS)
    
    print(f"Built extension JAR: {output_path}")


if __name__ == "__main__":
    build_jar("/app/extensions/openrefine-gdata.jar")
