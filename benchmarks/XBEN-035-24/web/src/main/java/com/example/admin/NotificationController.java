package com.example.admin;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.thymeleaf.context.Context;
import org.thymeleaf.spring5.SpringTemplateEngine;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.UUID;

/**
 * This controller simulates a notification system similar to Spring Boot Admin's MailNotifier.
 * Users can configure custom notification templates (like the mail.template property in SBA).
 * 
 * The vulnerability exists because:
 * 1. Users can specify a custom template path
 * 2. Users can write custom template content
 * 3. Thymeleaf processes the template without restricting static method access
 * 
 * This is a faithful recreation of CVE-2023-38286 where:
 * - MailNotifier allows custom template paths via spring.boot.admin.notify.mail.template
 * - Templates are processed by Thymeleaf's templateEngine.process()
 * - Thymeleaf < 3.1.2 allows access to static Java methods enabling RCE
 */
@Controller
public class NotificationController {

    @Autowired
    private SpringTemplateEngine templateEngine;

    private String notificationTemplate = "notification";
    
    @GetMapping("/")
    public String index(Model model) {
        model.addAttribute("currentTemplate", notificationTemplate);
        return "index";
    }

    @GetMapping("/settings")
    public String settings(Model model) {
        model.addAttribute("currentTemplate", notificationTemplate);
        return "settings";
    }

    /**
     * Endpoint to upload/create custom notification templates
     * Similar to how Spring Boot Admin allows custom mail templates via configuration
     */
    @PostMapping("/settings/template")
    public String uploadTemplate(
            @RequestParam("templateName") String templateName,
            @RequestParam("templateContent") String templateContent,
            Model model) {
        
        try {
            // Create templates directory if it doesn't exist
            File templatesDir = new File("/tmp/templates");
            if (!templatesDir.exists()) {
                templatesDir.mkdirs();
            }
            
            // Sanitize template name to prevent path traversal
            String safeName = templateName.replaceAll("[^a-zA-Z0-9_-]", "");
            if (safeName.isEmpty()) {
                safeName = "custom_" + UUID.randomUUID().toString().substring(0, 8);
            }
            
            // Write the custom template - VULNERABLE: no validation of template content
            File templateFile = new File(templatesDir, safeName + ".html");
            try (FileWriter writer = new FileWriter(templateFile)) {
                writer.write(templateContent);
            }
            
            // Set as the active notification template
            this.notificationTemplate = safeName;
            
            model.addAttribute("message", "Template '" + safeName + "' saved and activated successfully!");
            model.addAttribute("currentTemplate", notificationTemplate);
            
        } catch (IOException e) {
            model.addAttribute("error", "Failed to save template: " + e.getMessage());
            model.addAttribute("currentTemplate", notificationTemplate);
        }
        
        return "settings";
    }

    /**
     * Endpoint to preview notification with current template
     * This is where the SSTI vulnerability is triggered - similar to MailNotifier.getBody()
     * 
     * The vulnerability (CVE-2023-38286):
     * templateEngine.process(this.template, ctx) evaluates Thymeleaf expressions
     * including T() expressions that access Java static methods
     */
    @GetMapping("/notification/preview")
    public String previewNotification(Model model) {
        try {
            Context context = new Context();
            context.setVariable("appName", "Sample Application");
            context.setVariable("status", "UP");
            context.setVariable("timestamp", java.time.LocalDateTime.now().toString());
            
            // Process the template - VULNERABLE: processes user-controlled template
            // This is equivalent to MailNotifier.getBody() which calls:
            // templateEngine.process(this.template, ctx)
            String processedContent = templateEngine.process(notificationTemplate, context);
            
            model.addAttribute("previewContent", processedContent);
            model.addAttribute("templateName", notificationTemplate);
            
        } catch (Exception e) {
            model.addAttribute("error", "Template processing error: " + e.getMessage());
            model.addAttribute("templateName", notificationTemplate);
        }
        
        return "preview";
    }

    /**
     * Endpoint to change the active template path
     * Similar to setting spring.boot.admin.notify.mail.template
     */
    @PostMapping("/settings/template-path")
    public String setTemplatePath(
            @RequestParam("templatePath") String templatePath,
            Model model) {
        
        // Basic validation - but still allows custom templates in /tmp/templates/
        if (templatePath != null && !templatePath.isEmpty()) {
            this.notificationTemplate = templatePath.replaceAll("[^a-zA-Z0-9_-]", "");
        }
        
        model.addAttribute("message", "Active template set to: " + this.notificationTemplate);
        model.addAttribute("currentTemplate", notificationTemplate);
        
        return "settings";
    }
}
