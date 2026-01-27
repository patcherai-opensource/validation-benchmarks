package com.example.admin;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.ApplicationContext;
import org.springframework.expression.Expression;
import org.springframework.expression.ExpressionParser;
import org.springframework.expression.spel.standard.SpelExpressionParser;
import org.springframework.expression.spel.support.StandardEvaluationContext;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.thymeleaf.context.Context;
import org.thymeleaf.spring5.SpringTemplateEngine;
import org.thymeleaf.spring5.expression.ThymeleafEvaluationContext;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

@Controller
public class NotificationController {

    @Autowired
    private SpringTemplateEngine templateEngine;
    
    @Autowired
    private ApplicationContext applicationContext;
    
    private final ExpressionParser spelParser = new SpelExpressionParser();

    @GetMapping("/")
    public String index(Model model) {
        model.addAttribute("appName", "Admin Monitor");
        return "index";
    }

    @GetMapping("/notifications")
    public String notifications(Model model) {
        model.addAttribute("defaultTemplate", "<div>Application <span th:text=\"${name}\"></span> status changed to <span th:text=\"${status}\"></span></div>");
        return "notifications";
    }

    @PostMapping("/notifications/preview")
    @ResponseBody
    public String previewNotification(@RequestParam("template") String template,
                                       @RequestParam(value = "appName", defaultValue = "TestApp") String appName,
                                       @RequestParam(value = "status", defaultValue = "UP") String status) {
        try {
            // First, process any SpEL expressions in __${...}__ format (VULNERABLE)
            String processedTemplate = processSpelExpressions(template, appName, status);
            
            // Then process with Thymeleaf for standard template features
            Context context = new Context();
            context.setVariable("name", appName);
            context.setVariable("status", status);
            
            // Enable full SpEL evaluation context (VULNERABLE)
            ThymeleafEvaluationContext evalContext = new ThymeleafEvaluationContext(applicationContext, null);
            context.setVariable(ThymeleafEvaluationContext.THYMELEAF_EVALUATION_CONTEXT_CONTEXT_VARIABLE_NAME, evalContext);
            
            String result = templateEngine.process(processedTemplate, context);
            
            return "{\"success\": true, \"preview\": \"" + escapeJson(result) + "\"}";
        } catch (Exception e) {
            String errorMsg = e.getMessage();
            if (e.getCause() != null) {
                errorMsg += " Caused by: " + e.getCause().getMessage();
            }
            return "{\"success\": false, \"error\": \"" + escapeJson(errorMsg) + "\"}";
        }
    }
    
    /**
     * Process custom SpEL expressions in format __${expression}__
     * VULNERABLE: Allows arbitrary SpEL execution including:
     * - File read: T(java.nio.file.Files).readString(T(java.nio.file.Paths).get('/tmp/flag'))
     * - RCE: T(java.lang.Runtime).getRuntime().exec('command')
     * - System properties: T(java.lang.System).getProperty('user.dir')
     */
    private String processSpelExpressions(String template, String appName, String status) {
        Pattern pattern = Pattern.compile("__\\$\\{(.+?)\\}__");
        Matcher matcher = pattern.matcher(template);
        StringBuffer result = new StringBuffer();
        
        StandardEvaluationContext evalContext = new StandardEvaluationContext();
        evalContext.setVariable("name", appName);
        evalContext.setVariable("status", status);
        
        while (matcher.find()) {
            String expression = matcher.group(1);
            try {
                Expression exp = spelParser.parseExpression(expression);
                Object value = exp.getValue(evalContext);
                String replacement = value != null ? value.toString() : "";
                matcher.appendReplacement(result, Matcher.quoteReplacement(replacement));
            } catch (Exception e) {
                matcher.appendReplacement(result, "[SpEL Error: " + Matcher.quoteReplacement(e.getMessage()) + "]");
            }
        }
        matcher.appendTail(result);
        return result.toString();
    }

    @PostMapping("/notifications/save")
    @ResponseBody
    public String saveNotification(@RequestParam("template") String template) {
        return "{\"success\": true, \"message\": \"Template saved successfully\"}";
    }

    private String escapeJson(String str) {
        if (str == null) return "";
        return str.replace("\\", "\\\\")
                  .replace("\"", "\\\"")
                  .replace("\n", "\\n")
                  .replace("\r", "\\r")
                  .replace("\t", "\\t");
    }
}
