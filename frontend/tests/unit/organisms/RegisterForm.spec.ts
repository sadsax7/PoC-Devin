/**
 * @fileoverview Tests for the RegisterForm organism component (SSR render).
 *
 * Tests the static HTML output (initial render state) of the form.
 * Hook-dependent behaviour (useRegister) is mocked where needed.
 *
 * Covers all 7 mandatory test types defined in FRONTEND-GUIDELINES.md §7.3.2.
 *
 * @remarks
 * Pattern: AAA (Arrange-Act-Assert).
 * Naming: should_<expected>_when_<condition>.
 */

import { expect } from 'chai';
import React from 'react';
import ReactDOMServer from 'react-dom/server';
import { RegisterForm } from '../../../src/components/organisms/RegisterForm';

describe('RegisterForm (SSR)', () => {
  // ---------------------------------------------------------------
  // 1. Positive cases (happy path)
  // ---------------------------------------------------------------
  describe('Positive cases', () => {
    it('should_render_form_with_all_required_fields', () => {
      // Arrange
      const element = React.createElement(RegisterForm, {});

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('id="phone"');
      expect(html).to.contain('id="password"');
      expect(html).to.contain('id="confirm_password"');
      expect(html).to.contain('id="email"');
      expect(html).to.contain('id="name"');
    });

    it('should_render_submit_button', () => {
      // Arrange
      const element = React.createElement(RegisterForm, {});

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('Registrarse');
    });

    it('should_render_logo_image', () => {
      // Arrange
      const element = React.createElement(RegisterForm, {});

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('src="/next.svg"');
      expect(html).to.contain('alt="Billetera Virtual logo"');
    });

    it('should_render_heading', () => {
      // Arrange
      const element = React.createElement(RegisterForm, {});

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('Crear cuenta');
    });
  });

  // ---------------------------------------------------------------
  // 2. Negative cases (error handling)
  // ---------------------------------------------------------------
  describe('Negative cases', () => {
    it('should_disable_submit_button_initially', () => {
      // Arrange — form is empty → button disabled
      const element = React.createElement(RegisterForm, {});

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('disabled');
    });

    it('should_not_crash_when_no_props_provided', () => {
      // Arrange
      const element = React.createElement(RegisterForm);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('<form');
    });
  });

  // ---------------------------------------------------------------
  // 3. Edge cases
  // ---------------------------------------------------------------
  describe('Edge cases', () => {
    it('should_render_with_empty_className', () => {
      // Arrange
      const element = React.createElement(RegisterForm, { className: '' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('<section');
    });

    it('should_render_phone_placeholder', () => {
      // Arrange
      const element = React.createElement(RegisterForm, {});

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('placeholder="ej: +573001234567"');
    });

    it('should_render_email_placeholder', () => {
      // Arrange
      const element = React.createElement(RegisterForm, {});

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('placeholder="user@example.com"');
    });
  });

  // ---------------------------------------------------------------
  // 4. Interaction cases
  // ---------------------------------------------------------------
  describe('Interaction cases', () => {
    it('should_render_password_toggle_buttons', () => {
      // Arrange
      const element = React.createElement(RegisterForm, {});

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert — two toggle buttons (password + confirm)
      expect(html).to.contain('Mostrar contraseña');
      expect(html).to.contain('Mostrar confirmación');
    });

    it('should_render_login_link_button', () => {
      // Arrange
      const element = React.createElement(RegisterForm, {});

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('¿Ya tienes cuenta?');
      expect(html).to.contain('Ingresar');
      expect(html).to.contain('href="/auth/login"');
    });
  });

  // ---------------------------------------------------------------
  // 5. State transition cases
  // ---------------------------------------------------------------
  describe('State transition cases', () => {
    it('should_render_form_section_initially_not_success', () => {
      // Arrange
      const element = React.createElement(RegisterForm, {});

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert — should not show success overlay
      expect(html).to.not.contain('¡Cuenta creada exitosamente!');
      expect(html).to.contain('Formulario de registro');
    });

    it('should_show_password_strength_indicator', () => {
      // Arrange — empty password → none strength
      const element = React.createElement(RegisterForm, {});

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('role="progressbar"');
    });
  });

  // ---------------------------------------------------------------
  // 6. Accessibility cases
  // ---------------------------------------------------------------
  describe('Accessibility cases', () => {
    it('should_have_aria_label_on_section', () => {
      // Arrange
      const element = React.createElement(RegisterForm, {});

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('aria-label="Formulario de registro"');
    });

    it('should_have_labels_for_all_inputs', () => {
      // Arrange
      const element = React.createElement(RegisterForm, {});

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('for="phone"');
      expect(html).to.contain('for="password"');
      expect(html).to.contain('for="confirm_password"');
      expect(html).to.contain('for="email"');
      expect(html).to.contain('for="name"');
    });

    it('should_have_noValidate_on_form', () => {
      // Arrange
      const element = React.createElement(RegisterForm, {});

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('novalidate');
    });

    it('should_render_password_fields_as_password_type', () => {
      // Arrange
      const element = React.createElement(RegisterForm, {});

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert — initial state has password type
      expect(html).to.contain('type="password"');
    });
  });

  // ---------------------------------------------------------------
  // 7. Props variations
  // ---------------------------------------------------------------
  describe('Props variations', () => {
    it('should_apply_custom_className', () => {
      // Arrange
      const element = React.createElement(RegisterForm, { className: 'my-form' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('my-form');
    });

    it('should_use_custom_logo_src', () => {
      // Arrange
      const element = React.createElement(RegisterForm, { logoSrc: '/custom-logo.png' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('src="/custom-logo.png"');
    });

    it('should_use_custom_logo_alt', () => {
      // Arrange
      const element = React.createElement(RegisterForm, { logoAlt: 'My App' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('alt="My App"');
    });

    it('should_render_email_field_as_email_type', () => {
      // Arrange
      const element = React.createElement(RegisterForm, {});

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('type="email"');
    });
  });
});
