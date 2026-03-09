/**
 * @fileoverview Tests for the Home (Landing) page.
 *
 * Validates that the page correctly renders the HeroSection organism
 * with all default props as specified in HU-FE-01.
 *
 * @remarks
 * Pattern: AAA (Arrange-Act-Assert).
 * FRONTEND-GUIDELINES.md §3.5 — Pages: only assemble, no logic.
 */

import { expect } from 'chai';
import React from 'react';
import ReactDOMServer from 'react-dom/server';
import Home from '../../../src/app/page';

describe('Home Page', () => {
  // ---------------------------------------------------------------
  // 1. Positive cases
  // ---------------------------------------------------------------
  describe('Positive cases', () => {
    it('should_render_hero_section_with_welcome_title', () => {
      // Arrange
      const element = React.createElement(Home);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('Bienvenido a Billetera Virtual');
    });

    it('should_render_hero_section_with_subtitle', () => {
      // Arrange
      const element = React.createElement(Home);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('Tu dinero seguro, rápido y fácil de usar');
    });

    it('should_render_ingresar_button', () => {
      // Arrange
      const element = React.createElement(Home);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('Ingresar');
      expect(html).to.contain('href="/auth/login"');
    });

    it('should_render_registrarse_button', () => {
      // Arrange
      const element = React.createElement(Home);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('Registrarse');
      expect(html).to.contain('href="/auth/register"');
    });
  });

  // ---------------------------------------------------------------
  // 2. Negative cases
  // ---------------------------------------------------------------
  describe('Negative cases', () => {
    it('should_not_render_old_styleguide_link', () => {
      // Arrange
      const element = React.createElement(Home);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert — old placeholder content should be gone
      expect(html).to.not.contain('Ver Styleguide');
      expect(html).to.not.contain('href="/styleguide"');
    });

    it('should_not_render_old_placeholder_title', () => {
      // Arrange
      const element = React.createElement(Home);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.not.contain('PoC — Sprint 1');
    });
  });

  // ---------------------------------------------------------------
  // 3. Edge cases
  // ---------------------------------------------------------------
  describe('Edge cases', () => {
    it('should_render_without_any_props', () => {
      // Arrange & Act
      const element = React.createElement(Home);
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert — page takes no props; should render cleanly
      expect(html).to.contain('<section');
    });
  });

  // ---------------------------------------------------------------
  // 4. Structure / composition
  // ---------------------------------------------------------------
  describe('Composition', () => {
    it('should_render_a_single_section_element', () => {
      // Arrange
      const element = React.createElement(Home);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      const sectionCount = (html.match(/<section/g) || []).length;
      expect(sectionCount).to.equal(1);
    });

    it('should_contain_logo_image', () => {
      // Arrange
      const element = React.createElement(Home);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('<img');
      expect(html).to.contain('src="/next.svg"');
    });
  });

  // ---------------------------------------------------------------
  // 5. Accessibility
  // ---------------------------------------------------------------
  describe('Accessibility', () => {
    it('should_have_h1_heading', () => {
      // Arrange
      const element = React.createElement(Home);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('<h1');
    });

    it('should_have_aria_label_on_section', () => {
      // Arrange
      const element = React.createElement(Home);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('aria-label="Hero section"');
    });
  });
});

