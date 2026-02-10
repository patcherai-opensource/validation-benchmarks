# Wagtail-Style ModelAdmin Stored XSS Challenge

A simulation of the stored XSS vulnerability found in Wagtail's ModelAdmin interface.

## Vulnerability Description

This challenge simulates CVE-like stored XSS vulnerability in a Wagtail-style CMS admin interface:

- **Vulnerable Component**: ModelAdmin views (InspectView and ChooseParentView)
- **Vulnerability Type**: Stored Cross-Site Scripting (XSS)
- **Attack Vector**: Malicious content in page titles rendered without proper escaping using `mark_safe`

## Scenario

1. Editors can create pages with arbitrary titles
2. Page titles are stored and later rendered in admin views
3. The titles are marked as safe HTML using `mark_safe` without escaping
4. When an admin views these pages, any malicious JavaScript in the title executes

## Exploitation Flow

1. Login as editor (editor / editor123)
2. Create a page with a malicious XSS payload in the title
3. Login as admin (admin / admin123)
4. View the created page via "Inspect" or "Choose Parent" actions
5. The XSS executes and the flag is revealed

## Technical Details

The vulnerability is triggered by:
- `mark_safe('<h2 class="page-title">{}</h2>'.format(page_data['title']))` in InspectView
- `mark_safe(' &gt; '.join(breadcrumb_parts))` in ChooseParentView breadcrumbs

This mirrors the actual Wagtail CVE where `mark_safe` was used on user-controlled titles.

## Goal

Execute `alert('XSS')` in the admin's browser context to retrieve the flag.
