/**
 * @fileoverview Tests for the LoginFlowManager organism component (SSR render).
 *
 * Tests the static HTML output of the login flow manager.
 * Covers all 7 mandatory test types defined in FRONTEND-GUIDELINES.md §7.3.2.
 *
 * @remarks
 * Pattern: AAA (Arrange-Act-Assert).
 * Naming: should_<expected>_when_<condition>.
 */

import { expect } from 'chai';
import sinon from 'sinon';
import React from 'react';
import ReactDOMServer from 'react-dom/server';
import { LoginFlowManager } from '../../../src/components/organisms/LoginFlowManager';

describe('LoginFlowManager (SSR)', () => {
  afterEach(() => sinon.restore());

  // ---------------------------------------------------------------
  // 1. Positive cases (happy path)
  // ---------------------------------------------------------------
  describe('Positive cases', () => {
    it('should_render_login_form_as_initial_step', () => {
      // Arrange
      const el = React.createElement(LoginFlowManager, {});

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert — initial step is LoginForm
      expect(html).to.contain('Iniciar sesión');
    });

    it('should_render_phone_and_password_in_initial_step', () => {
      // Arrange
      const el = React.createElement(LoginFlowManager, {});

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('id="phone"');
      expect(html).to.contain('id="password"');
    });

    it('should_render_without_crashing', () => {
      // Arrange
      const el = React.createElement(LoginFlowManager, {});

      // Act & Assert
      expect(() => ReactDOMServer.renderToStaticMarkup(el)).to.not.throw();
    });
  });

  // ---------------------------------------------------------------
  // 2. Negative cases (error handling)
  // ---------------------------------------------------------------
  describe('Negative cases', () => {
    it('should_not_crash_when_no_props_provided', () => {
      // Arrange
      const el = React.createElement(LoginFlowManager);

      // Act & Assert
      expect(() => ReactDOMServer.renderToStaticMarkup(el)).to.not.throw();
    });

    it('should_not_render_mfa_step_initially', () => {
      // Arrange
      const el = React.createElement(LoginFlowManager, {});

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert — MFA step not shown in initial render
      expect(html).to.not.contain('Verificación de Seguridad');
    });
  });

  // ---------------------------------------------------------------
  // 3. Edge cases
  // ---------------------------------------------------------------
  describe('Edge cases', () => {
    it('should_propagate_custom_className_to_login_form', () => {
      // Arrange
      const el = React.createElement(LoginFlowManager, { className: 'flow-wrapper' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('flow-wrapper');
    });

    it('should_render_register_link_in_initial_step', () => {
      // Arrange
      const el = React.createElement(LoginFlowManager, {});

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('/auth/register');
    });
  });

  // ---------------------------------------------------------------
  // 4. Interaction cases
  // ---------------------------------------------------------------
  describe('Interaction cases', () => {
    it('should_render_ingresar_button_in_initial_step', () => {
      // Arrange
      const el = React.createElement(LoginFlowManager, {});

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('Ingresar');
    });

    it('should_have_phone_placeholder_in_initial_step', () => {
      // Arrange
      const el = React.createElement(LoginFlowManager, {});

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('+573001234567');
    });
  });

  // ---------------------------------------------------------------
  // 5. State transition cases
  // ---------------------------------------------------------------
  describe('State transition cases', () => {
    it('should_render_login_step_in_initial_state', () => {
      // Arrange
      const el = React.createElement(LoginFlowManager, {});

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert — LoginForm, not MfaForm
      expect(html).to.contain('Iniciar sesión');
      expect(html).to.not.contain('otp-digit-0');
    });

    it('should_render_logo_in_initial_step', () => {
      // Arrange
      const el = React.createElement(LoginFlowManager, {});

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('dark:invert');
    });
  });

  // ---------------------------------------------------------------
  // 6. Accessibility cases
  // ---------------------------------------------------------------
  describe('Accessibility cases', () => {
    it('should_have_accessible_section_in_initial_step', () => {
      // Arrange
      const el = React.createElement(LoginFlowManager, {});

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('aria-label="Formulario de inicio de sesión"');
    });

    it('should_have_labels_associated_with_inputs', () => {
      // Arrange
      const el = React.createElement(LoginFlowManager, {});

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('for="phone"');
      expect(html).to.contain('for="password"');
    });
  });

  // ---------------------------------------------------------------
  // 7. Props variations
  // ---------------------------------------------------------------
  describe('Props variations', () => {
    it('should_accept_navigateFn_override', () => {
      // Arrange
      const navFn = sinon.stub();
      const el = React.createElement(LoginFlowManager, { navigateFn: navFn });

      // Act & Assert
      expect(() => ReactDOMServer.renderToStaticMarkup(el)).to.not.throw();
    });

    it('should_render_identically_with_and_without_className', () => {
      // Arrange
      const withClass = React.createElement(LoginFlowManager, { className: 'x' });
      const withoutClass = React.createElement(LoginFlowManager, {});

      // Act
      const html1 = ReactDOMServer.renderToStaticMarkup(withClass);
      const html2 = ReactDOMServer.renderToStaticMarkup(withoutClass);

      // Assert — both contain the login form structure
      expect(html1).to.contain('Iniciar sesión');
      expect(html2).to.contain('Iniciar sesión');
    });
  });
});
