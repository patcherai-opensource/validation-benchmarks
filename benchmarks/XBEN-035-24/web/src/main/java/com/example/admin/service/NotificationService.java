package com.example.admin.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Service;
import org.thymeleaf.TemplateEngine;
import org.thymeleaf.context.Context;
import org.thymeleaf.spring5.SpringTemplateEngine;

import java.util.Map;

@Service
public class NotificationService {

    @Autowired
    private SpringTemplateEngine templateEngine;

    @Autowired
    @Qualifier("inlineTemplateEngine")
    private TemplateEngine inlineTemplateEngine;

    public String processTemplate(String templateContent, Map<String, Object> variables) {
        Context context = new Context();
        if (variables != null) {
            variables.forEach(context::setVariable);
        }
        return inlineTemplateEngine.process(templateContent, context);
    }

    public String renderNotification(String templateName, Map<String, Object> variables) {
        Context context = new Context();
        if (variables != null) {
            variables.forEach(context::setVariable);
        }
        return templateEngine.process(templateName, context);
    }
}
