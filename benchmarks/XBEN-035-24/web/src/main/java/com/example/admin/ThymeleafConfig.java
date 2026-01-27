package com.example.admin;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;
import org.thymeleaf.spring5.SpringTemplateEngine;
import org.thymeleaf.spring5.templateresolver.SpringResourceTemplateResolver;
import org.thymeleaf.templatemode.TemplateMode;
import org.thymeleaf.templateresolver.StringTemplateResolver;
import org.springframework.context.ApplicationContext;
import org.springframework.beans.factory.annotation.Autowired;
import org.thymeleaf.standard.StandardDialect;

@Configuration
public class ThymeleafConfig {

    @Autowired
    private ApplicationContext applicationContext;

    @Bean
    @Primary
    public SpringTemplateEngine templateEngine() {
        SpringTemplateEngine engine = new SpringTemplateEngine();
        
        // Add string template resolver for processing dynamic templates (VULNERABLE)
        StringTemplateResolver stringResolver = new StringTemplateResolver();
        stringResolver.setTemplateMode(TemplateMode.HTML);
        stringResolver.setOrder(1);
        stringResolver.setCacheable(false);
        
        // Add Spring resource resolver for static templates
        SpringResourceTemplateResolver resourceResolver = new SpringResourceTemplateResolver();
        resourceResolver.setApplicationContext(applicationContext);
        resourceResolver.setPrefix("classpath:/templates/");
        resourceResolver.setSuffix(".html");
        resourceResolver.setTemplateMode(TemplateMode.HTML);
        resourceResolver.setOrder(2);
        resourceResolver.setCheckExistence(true);
        resourceResolver.setCacheable(false);
        
        engine.addTemplateResolver(stringResolver);
        engine.addTemplateResolver(resourceResolver);
        
        // Enable SpringEL compiler - this is KEY for SSTI exploitation
        engine.setEnableSpringELCompiler(true);
        
        // Configure dialect with unrestricted expression mode (VULNERABLE)
        StandardDialect dialect = new StandardDialect();
        engine.setDialect(dialect);
        
        return engine;
    }
}
