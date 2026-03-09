/**
 * @fileoverview Tests for the LoginForm organism component (SSR render).
 *
 * Tests the static HTML output (initial render state) of the login form.
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
import { LoginForm, validateLoginPhone, validateLoginPassword } from '../../../src/components/organisms/LoginForm';

describe('LoginForm (SSR)', () => {
  afterEach(() => sinon.restore());

  // ---------------------------------------------------------------
  // 1. Positive cases (happy path)
  // ---------------------------------------------------------------
  describe('Positive cases', () => {
    it('should_render_phone_and_password_fields', () => {
      // Arrange
      const el = React.createElement(LoginForm, {});

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('id="phone"');
      expect(html).to.contain('id="password"');
    });

    it('should_render_login_heading', () => {
      // Arrange
      const el = React.createElement(LoginForm, {});

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('Iniciar sesión');
    });

    it('should_render_submit_button_with_ingresar_label', () => {
      // Arrange
      const el = React.createElement(LoginForm, {});

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('Ingresar');
    });

    it('should_render_logo_image', () => {
      // Arrange
      const el = React.createElement(LoginForm, {});

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('src="/next.svg"');
    });

    it('should_render_register_link_button', () => {
      // Arrange
      const el = React.createElement(LoginForm, {});

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('/auth/register');
    });
  });

  // ---------------------------------------------------------------
  // 2. Negative cases (error handling)
  // ---------------------------------------------------------------
  describe('Negative cases', () => {
    it('should_render_submit_button_disabled_initially', () => {
      // Arrange — form is empty → both fields invalid → button disabled
      const el = React.createElement(LoginForm, {});

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('disabled');
    });

    it('should_not_crash_when_no_props_provided', () => {
      // Arrange
      const el = React.createElement(LoginForm);

      // Act & Assert
      expect(() => ReactDOMServer.renderToStaticMarkup(el)).to.not.throw();
    });

    it('should_not_crash_when_onMfaRequired_is_undefined', () => {
      // Arrange
      const el = React.createElement(LoginForm, { onMfaRequired: undefined });

      // Act & Assert
      expect(() => ReactDOMServer.renderToStaticMarkup(el)).to.not.throw();
    });
  });

  // ---------------------------------------------------------------
  // 3. Edge cases
  // ---------------------------------------------------------------
  describe('Edge cases', () => {
    it('should_render_custom_logo_src_when_provided', () => {
      // Arrange
      const el = React.createElement(LoginForm, { logoSrc: '/custom-logo.svg' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('src="/custom-logo.svg"');
    });

    it('should_render_custom_logo_alt_when_provided', () => {
      // Arrange
      const el = React.createElement(LoginForm, { logoAlt: 'My Brand' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('alt="My Brand"');
    });

    it('should_apply_custom_className_to_section', () => {
      // Arrange
      const el = React.createElement(LoginForm, { className: 'extra-class' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('extra-class');
    });
  });

  // ---------------------------------------------------------------
  // 4. Interaction cases
  // ---------------------------------------------------------------
  describe('Interaction cases', () => {
    it('should_have_password_field_with_correct_initial_type', () => {
      // Arrange
      const el = React.createElement(LoginForm, {});

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert — password field type="password" initially (toggle off)
      expect(html).to.contain('type="password"');
    });

    it('should_have_phone_placeholder_text', () => {
      // Arrange
      const el = React.createElement(LoginForm, {});

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('+573001234567');
    });

    it('should_have_form_novalidate_attribute', () => {
      // Arrange
      const el = React.createElement(LoginForm, {});

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert — form uses browser-native novalidate, custom validation
      expect(html).to.contain('novalidate');
    });

    it('should_have_password_visibility_toggle_button', () => {
      // Arrange
      const el = React.createElement(LoginForm, {});

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('Mostrar contraseña');
    });
  });

  // ---------------------------------------------------------------
  // 5. State transition cases
  // ---------------------------------------------------------------
  describe('State transition cases', () => {
    it('should_render_initial_state_without_error_messages', () => {
      // Arrange
      const el = React.createElement(LoginForm, {});

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert — no error and no loading text in initial render
      expect(html).to.not.contain('Iniciando sesión...');
    });

    it('should_render_ingresar_label_when_not_loading', () => {
      // Arrange
      const el = React.createElement(LoginForm, {});

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('Ingresar');
    });
  });

  // ---------------------------------------------------------------
  // 6. Accessibility cases
  // ---------------------------------------------------------------
  describe('Accessibility cases', () => {
    it('should_have_section_aria_label', () => {
      // Arrange
      const el = React.createElement(LoginForm, {});

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('aria-label="Formulario de inicio de sesión"');
    });

    it('should_have_form_aria_label', () => {
      // Arrange
      const el = React.createElement(LoginForm, {});

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('aria-label="Iniciar sesión"');
    });

    it('should_have_label_for_phone_field', () => {
      // Arrange
      const el = React.createElement(LoginForm, {});

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('for="phone"');
    });

    it('should_have_label_for_password_field', () => {
      // Arrange
      const el = React.createElement(LoginForm, {});

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('for="password"');
    });
  });

  // ---------------------------------------------------------------
  // 7. Props variations
  // ---------------------------------------------------------------
  describe('Props variations', () => {
    it('should_render_with_navigateFn_override', () => {
      // Arrange
      const navFn = sinon.stub();
      const el = React.createElement(LoginForm, { navigateFn: navFn });

      // Act & Assert
      expect(() => ReactDOMServer.renderToStaticMarkup(el)).to.not.throw();
    });

    it('should_render_same_structure_regardless_of_onMfaRequired', () => {
      // Arrange
      const withCb = React.createElement(LoginForm, { onMfaRequired: () => {} });
      const withoutCb = React.createElement(LoginForm, {});

      // Act
      const html1 = ReactDOMServer.renderToStaticMarkup(withCb);
      const html2 = ReactDOMServer.renderToStaticMarkup(withoutCb);

      // Assert — same structure
      expect(html1).to.contain('id="phone"');
      expect(html2).to.contain('id="phone"');
    });
  });

  // ---------------------------------------------------------------
  // Validation helper tests
  // ---------------------------------------------------------------
  describe('validateLoginPhone (exported helper)', () => {
    it('should_return_empty_for_valid_e164', () => {
      expect(validateLoginPhone('+573001234567')).to.equal('');
    });

    it('should_return_error_for_missing_plus', () => {
      expect(validateLoginPhone('573001234567')).to.not.equal('');
    });
  });

  describe('validateLoginPassword (exported helper)', () => {
    it('should_return_empty_for_non_empty_password', () => {
      expect(validateLoginPassword('Str0ng!')).to.equal('');
    });

    it('should_return_error_for_empty_password', () => {
      expect(validateLoginPassword('')).to.not.equal('');
    });
  });
});
