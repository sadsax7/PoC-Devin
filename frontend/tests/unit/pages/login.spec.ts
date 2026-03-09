/**
 * @fileoverview Tests for the /auth/login page.
 *
 * Verifies the page correctly assembles the LoginFlowManager organism
 * in accordance with the "Thin Page" pattern.
 *
 * @remarks
 * Pattern: AAA (Arrange-Act-Assert).
 * Naming: should_<expected>_when_<condition>.
 */

import { expect } from 'chai';
import React from 'react';
import ReactDOMServer from 'react-dom/server';
import LoginPage from '../../../src/app/auth/login/page';

describe('LoginPage (/auth/login)', () => {
  // ---------------------------------------------------------------
  // 1. Positive cases (happy path)
  // ---------------------------------------------------------------
  describe('Positive cases', () => {
    it('should_render_login_flow_manager_organism', () => {
      // Arrange
      const el = React.createElement(LoginPage);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert — LoginFlowManager renders LoginForm initially
      expect(html).to.contain('Iniciar sesión');
    });

    it('should_render_phone_and_password_fields', () => {
      // Arrange
      const el = React.createElement(LoginPage);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('id="phone"');
      expect(html).to.contain('id="password"');
    });

    it('should_render_logo_image', () => {
      // Arrange
      const el = React.createElement(LoginPage);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('/next.svg');
    });
  });

  // ---------------------------------------------------------------
  // 2. Negative cases
  // ---------------------------------------------------------------
  describe('Negative cases', () => {
    it('should_not_crash_when_rendered', () => {
      // Arrange & Act
      const html = ReactDOMServer.renderToStaticMarkup(React.createElement(LoginPage));

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
      expect(LoginPage).to.be.a('function');
    });

    it('should_not_render_mfa_form_initially', () => {
      // Arrange
      const el = React.createElement(LoginPage);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.not.contain('Verificación de Seguridad');
    });
  });

  // ---------------------------------------------------------------
  // 4. Interaction cases
  // ---------------------------------------------------------------
  describe('Interaction cases', () => {
    it('should_include_register_link', () => {
      // Arrange
      const el = React.createElement(LoginPage);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('href="/auth/register"');
    });
  });

  // ---------------------------------------------------------------
  // 5. State transition cases
  // ---------------------------------------------------------------
  describe('State transition cases', () => {
    it('should_render_initial_idle_state', () => {
      // Arrange
      const el = React.createElement(LoginPage);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert — submit text without loading
      expect(html).to.contain('Ingresar');
      expect(html).to.not.contain('Iniciando sesión...');
    });
  });

  // ---------------------------------------------------------------
  // 6. Accessibility cases
  // ---------------------------------------------------------------
  describe('Accessibility cases', () => {
    it('should_have_accessible_form', () => {
      // Arrange
      const el = React.createElement(LoginPage);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('aria-label');
    });
  });

  // ---------------------------------------------------------------
  // 7. Props variations
  // ---------------------------------------------------------------
  describe('Props variations', () => {
    it('should_render_without_any_props', () => {
      // Arrange & Act
      const html = ReactDOMServer.renderToStaticMarkup(React.createElement(LoginPage));

      // Assert
      expect(html).to.contain('<section');
    });
  });
});
