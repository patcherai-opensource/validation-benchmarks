package com.example.admin.controller;

import com.example.admin.service.NotificationService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@Controller
public class AdminController {

    @Autowired
    private NotificationService notificationService;

    @GetMapping("/")
    public String index(Model model) {
        return "index";
    }

    @GetMapping("/notifications")
    public String notifications(Model model) {
        return "notifications";
    }

    @GetMapping("/settings")
    public String settings(Model model) {
        return "settings";
    }

    @PostMapping("/notifications/preview")
    @ResponseBody
    public String previewNotification(@RequestParam("template") String template,
                                       @RequestParam(value = "appName", defaultValue = "My Application") String appName,
                                       @RequestParam(value = "status", defaultValue = "UP") String status) {
        Map<String, Object> vars = new HashMap<>();
        vars.put("appName", appName);
        vars.put("status", status);
        vars.put("timestamp", System.currentTimeMillis());
        
        try {
            return notificationService.processTemplate(template, vars);
        } catch (Exception e) {
            return "Error processing template";
        }
    }
}
