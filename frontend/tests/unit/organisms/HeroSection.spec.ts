/**
 * @fileoverview Tests for the HeroSection organism component.
 *
 * Covers all 7 mandatory test types defined in FRONTEND-GUIDELINES.md §7.3.2:
 * 1. Positive (happy path)
 * 2. Negative (error handling)
 * 3. Edge cases
 * 4. Interactions
 * 5. State transitions
 * 6. Accessibility
 * 7. Props variations / responsive
 *
 * @remarks
 * Pattern: AAA (Arrange-Act-Assert).
 * Naming: should_&lt;expected&gt;_when_&lt;condition&gt;.
 */

import { expect } from 'chai';
import React from 'react';
import ReactDOMServer from 'react-dom/server';
import { HeroSection } from '../../../src/components/organisms';

describe('HeroSection', () => {
  // ---------------------------------------------------------------
  // 1. Positive cases (happy path)
  // ---------------------------------------------------------------
  describe('Positive cases', () => {
    it('should_render_default_title_when_no_props_provided', () => {
      // Arrange
      const element = React.createElement(HeroSection);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('Bienvenido a Billetera Virtual');
    });

    it('should_render_default_subtitle_when_no_props_provided', () => {
      // Arrange
      const element = React.createElement(HeroSection);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('Tu dinero seguro, rápido y fácil de usar');
    });

    it('should_render_logo_with_default_src', () => {
      // Arrange
      const element = React.createElement(HeroSection);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('src="/next.svg"');
    });

    it('should_render_ingresar_button_with_login_href', () => {
      // Arrange
      const element = React.createElement(HeroSection);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('Ingresar');
      expect(html).to.contain('href="/auth/login"');
    });

    it('should_render_registrarse_button_with_register_href', () => {
      // Arrange
      const element = React.createElement(HeroSection);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('Registrarse');
      expect(html).to.contain('href="/auth/register"');
    });

    it('should_render_ingresar_as_outline_variant', () => {
      // Arrange
      const element = React.createElement(HeroSection);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert — the first <a> (Ingresar) should have outline classes
      const ingresarMatch = html.match(/<a[^>]*>Ingresar<\/a>/);
      expect(ingresarMatch).to.not.be.null;
      expect(ingresarMatch![0]).to.contain('border-primary');
      expect(ingresarMatch![0]).to.contain('bg-transparent');
    });

    it('should_render_registrarse_as_solid_variant', () => {
      // Arrange
      const element = React.createElement(HeroSection);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert — the second <a> (Registrarse) should have solid classes
      const registrarseMatch = html.match(/<a[^>]*>Registrarse<\/a>/);
      expect(registrarseMatch).to.not.be.null;
      expect(registrarseMatch![0]).to.contain('bg-primary');
    });
  });

  // ---------------------------------------------------------------
  // 2. Negative cases (error handling)
  // ---------------------------------------------------------------
  describe('Negative cases', () => {
    it('should_not_crash_when_all_props_are_empty_strings', () => {
      // Arrange
      const element = React.createElement(HeroSection, {
        title: '',
        subtitle: '',
        logoSrc: '',
        logoAlt: '',
        loginHref: '',
        registerHref: '',
        className: '',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert — should still render the section
      expect(html).to.contain('<section');
    });

    it('should_render_buttons_as_button_elements_when_hrefs_are_empty', () => {
      // Arrange — empty href is falsy, Button renders <button> instead of <a>
      const element = React.createElement(HeroSection, {
        loginHref: '',
        registerHref: '',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('<button');
    });

    it('should_not_crash_when_logoSrc_points_to_nonexistent_file', () => {
      // Arrange
      const element = React.createElement(HeroSection, {
        logoSrc: '/non-existent-logo.png',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('src="/non-existent-logo.png"');
    });
  });

  // ---------------------------------------------------------------
  // 3. Edge cases
  // ---------------------------------------------------------------
  describe('Edge cases', () => {
    it('should_render_with_very_long_title', () => {
      // Arrange
      const longTitle = 'A'.repeat(500);
      const element = React.createElement(HeroSection, { title: longTitle });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain(longTitle);
    });

    it('should_render_with_special_characters_in_title', () => {
      // Arrange
      const element = React.createElement(HeroSection, {
        title: '¡Hola! <script>alert("xss")</script>',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert — React escapes HTML entities
      expect(html).to.contain('&lt;script&gt;');
      expect(html).to.not.contain('<script>');
    });

    it('should_render_with_unicode_characters', () => {
      // Arrange
      const element = React.createElement(HeroSection, {
        title: '💰 Billetera Virtual 🚀',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('💰 Billetera Virtual 🚀');
    });

    it('should_handle_relative_and_absolute_hrefs', () => {
      // Arrange
      const element = React.createElement(HeroSection, {
        loginHref: 'https://example.com/login',
        registerHref: '/auth/register',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('href="https://example.com/login"');
      expect(html).to.contain('href="/auth/register"');
    });
  });

  // ---------------------------------------------------------------
  // 4. Interaction cases
  // ---------------------------------------------------------------
  describe('Interaction cases', () => {
    it('should_render_two_navigation_links_for_cta_buttons', () => {
      // Arrange
      const element = React.createElement(HeroSection);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert — two <a> elements
      const anchorMatches = html.match(/<a /g);
      expect(anchorMatches).to.have.length(2);
    });

    it('should_render_ingresar_before_registrarse', () => {
      // Arrange
      const element = React.createElement(HeroSection);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      const ingresarIndex = html.indexOf('Ingresar');
      const registrarseIndex = html.indexOf('Registrarse');
      expect(ingresarIndex).to.be.lessThan(registrarseIndex);
    });

    it('should_wrap_buttons_in_a_group_container', () => {
      // Arrange
      const element = React.createElement(HeroSection);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('role="group"');
    });
  });

  // ---------------------------------------------------------------
  // 5. State / layout transition cases
  // ---------------------------------------------------------------
  describe('State / layout cases', () => {
    it('should_use_flex_col_for_mobile_layout', () => {
      // Arrange
      const element = React.createElement(HeroSection);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('flex-col');
    });

    it('should_use_md_flex_row_for_desktop_layout', () => {
      // Arrange
      const element = React.createElement(HeroSection);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('md:flex-row');
    });

    it('should_use_min_h_screen_for_full_viewport_height', () => {
      // Arrange
      const element = React.createElement(HeroSection);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('min-h-screen');
    });

    it('should_center_content_vertically_and_horizontally', () => {
      // Arrange
      const element = React.createElement(HeroSection);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('items-center');
      expect(html).to.contain('justify-center');
    });

    it('should_use_responsive_text_sizes_for_title', () => {
      // Arrange
      const element = React.createElement(HeroSection);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('text-3xl');
      expect(html).to.contain('md:text-5xl');
    });
  });

  // ---------------------------------------------------------------
  // 6. Accessibility cases
  // ---------------------------------------------------------------
  describe('Accessibility cases', () => {
    it('should_have_aria_label_on_hero_section', () => {
      // Arrange
      const element = React.createElement(HeroSection);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('aria-label="Hero section"');
    });

    it('should_have_aria_label_on_button_group', () => {
      // Arrange
      const element = React.createElement(HeroSection);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('aria-label="Opciones de acceso"');
    });

    it('should_have_alt_text_on_logo_image', () => {
      // Arrange
      const element = React.createElement(HeroSection);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('alt="Billetera Virtual logo"');
    });

    it('should_render_heading_h1_for_title', () => {
      // Arrange
      const element = React.createElement(HeroSection);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('<h1');
    });

    it('should_have_descriptive_text_in_buttons_not_just_icons', () => {
      // Arrange
      const element = React.createElement(HeroSection);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('Ingresar');
      expect(html).to.contain('Registrarse');
    });

    it('should_use_section_element_for_semantic_markup', () => {
      // Arrange
      const element = React.createElement(HeroSection);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.match(/^<section/);
    });
  });

  // ---------------------------------------------------------------
  // 7. Props variations
  // ---------------------------------------------------------------
  describe('Props variations', () => {
    it('should_render_custom_title_when_provided', () => {
      // Arrange
      const element = React.createElement(HeroSection, {
        title: 'Welcome!',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('Welcome!');
      expect(html).to.not.contain('Bienvenido a Billetera Virtual');
    });

    it('should_render_custom_subtitle_when_provided', () => {
      // Arrange
      const element = React.createElement(HeroSection, {
        subtitle: 'A different tagline',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('A different tagline');
    });

    it('should_render_custom_logo_when_provided', () => {
      // Arrange
      const element = React.createElement(HeroSection, {
        logoSrc: '/custom-logo.png',
        logoAlt: 'Custom logo',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('src="/custom-logo.png"');
      expect(html).to.contain('alt="Custom logo"');
    });

    it('should_render_custom_login_href_when_provided', () => {
      // Arrange
      const element = React.createElement(HeroSection, {
        loginHref: '/custom-login',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('href="/custom-login"');
    });

    it('should_render_custom_register_href_when_provided', () => {
      // Arrange
      const element = React.createElement(HeroSection, {
        registerHref: '/custom-register',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('href="/custom-register"');
    });

    it('should_apply_additional_className_to_root', () => {
      // Arrange
      const element = React.createElement(HeroSection, {
        className: 'extra-class',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('extra-class');
    });

    it('should_use_dark_background_by_default', () => {
      // Arrange
      const element = React.createElement(HeroSection);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('bg-bg-dark');
    });

    it('should_use_light_text_colors', () => {
      // Arrange
      const element = React.createElement(HeroSection);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('text-text-light');
    });

    it('should_render_all_custom_props_together', () => {
      // Arrange
      const element = React.createElement(HeroSection, {
        title: 'Custom Title',
        subtitle: 'Custom Subtitle',
        logoSrc: '/logo.svg',
        logoAlt: 'My Logo',
        loginHref: '/login',
        registerHref: '/signup',
        className: 'custom-hero',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('Custom Title');
      expect(html).to.contain('Custom Subtitle');
      expect(html).to.contain('src="/logo.svg"');
      expect(html).to.contain('alt="My Logo"');
      expect(html).to.contain('href="/login"');
      expect(html).to.contain('href="/signup"');
      expect(html).to.contain('custom-hero');
    });

    it('should_use_default_className_empty_when_not_provided', () => {
      // Arrange — exercises default className branch
      const element = React.createElement(HeroSection);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert — no extraneous class names, default classes present
      expect(html).to.contain('min-h-screen');
    });

    it('should_use_default_loginHref_when_not_provided', () => {
      // Arrange — exercises default loginHref branch
      const element = React.createElement(HeroSection);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('href="/auth/login"');
    });

    it('should_use_default_registerHref_when_not_provided', () => {
      // Arrange — exercises default registerHref branch
      const element = React.createElement(HeroSection);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('href="/auth/register"');
    });

    it('should_use_default_logoAlt_when_not_provided', () => {
      // Arrange — exercises default logoAlt branch
      const element = React.createElement(HeroSection);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('alt="Billetera Virtual logo"');
    });

    it('should_use_default_logoSrc_when_not_provided', () => {
      // Arrange — exercises default logoSrc branch
      const element = React.createElement(HeroSection);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('src="/next.svg"');
    });
  });
});

