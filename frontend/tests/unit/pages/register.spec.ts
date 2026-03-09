/**
 * @fileoverview Tests for the /auth/register page.
 *
 * Verifies the page assembles the RegisterForm organism correctly
 * without containing its own logic (Thin Page pattern).
 *
 * @remarks
 * Pattern: AAA (Arrange-Act-Assert).
 * Naming: should_<expected>_when_<condition>.
 */

import { expect } from 'chai';
import React from 'react';
import ReactDOMServer from 'react-dom/server';
import RegisterPage from '../../../src/app/auth/register/page';

describe('RegisterPage (/auth/register)', () => {
  // ---------------------------------------------------------------
  // 1. Positive cases (happy path)
  // ---------------------------------------------------------------
  describe('Positive cases', () => {
    it('should_render_register_form_organism', () => {
      // Arrange
      const element = React.createElement(RegisterPage);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert — RegisterForm renders a <section> with the form
      expect(html).to.contain('<section');
      expect(html).to.contain('Formulario de registro');
    });

    it('should_render_phone_field', () => {
      // Arrange
      const element = React.createElement(RegisterPage);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('id="phone"');
    });
  });

  // ---------------------------------------------------------------
  // 2. Negative cases
  // ---------------------------------------------------------------
  describe('Negative cases', () => {
    it('should_not_crash_when_rendered', () => {
      // Arrange & Act
      const html = ReactDOMServer.renderToStaticMarkup(React.createElement(RegisterPage));

      // Assert
      expect(html).to.be.a('string');
      expect(html.length).to.be.greaterThan(0);
    });
  });

  // ---------------------------------------------------------------
  // 3. Edge cases
  // ---------------------------------------------------------------
  describe('Edge cases', () => {
    it('should_be_a_function_component', () => {
      // Assert
      expect(RegisterPage).to.be.a('function');
    });
  });

  // ---------------------------------------------------------------
  // 4. Interaction cases
  // ---------------------------------------------------------------
  describe('Interaction cases', () => {
    it('should_include_login_link', () => {
      // Arrange
      const element = React.createElement(RegisterPage);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('href="/auth/login"');
    });
  });

  // ---------------------------------------------------------------
  // 5. State transition cases
  // ---------------------------------------------------------------
  describe('State transition cases', () => {
    it('should_render_initial_idle_state', () => {
      // Arrange
      const element = React.createElement(RegisterPage);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert — submit button present, no success message
      expect(html).to.contain('Registrarse');
      expect(html).to.not.contain('¡Cuenta creada exitosamente!');
    });
  });

  // ---------------------------------------------------------------
  // 6. Accessibility cases
  // ---------------------------------------------------------------
  describe('Accessibility cases', () => {
    it('should_have_form_with_aria_label', () => {
      // Arrange
      const element = React.createElement(RegisterPage);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('aria-label="Formulario de registro"');
    });
  });

  // ---------------------------------------------------------------
  // 7. Props variations
  // ---------------------------------------------------------------
  describe('Props variations', () => {
    it('should_render_without_any_props', () => {
      // Arrange
      const element = React.createElement(RegisterPage);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('<form');
    });
  });
});
