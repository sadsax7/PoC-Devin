/**
 * @fileoverview Tests for the MfaForm organism component (SSR render).
 *
 * Tests the static HTML output (initial render state) of the MFA form.
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
import { MfaForm } from '../../../src/components/organisms/MfaForm';

describe('MfaForm (SSR)', () => {
  afterEach(() => sinon.restore());

  // ---------------------------------------------------------------
  // 1. Positive cases (happy path)
  // ---------------------------------------------------------------
  describe('Positive cases', () => {
    it('should_render_six_otp_inputs', () => {
      // Arrange
      const el = React.createElement(MfaForm, { tempToken: 'token.abc' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      for (let i = 0; i < 6; i++) {
        expect(html).to.contain(`id="otp-digit-${i}"`);
      }
    });

    it('should_render_security_verification_heading', () => {
      // Arrange
      const el = React.createElement(MfaForm, { tempToken: 'token.abc' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('Verificación de Seguridad');
    });

    it('should_render_submit_button_with_verificar_label', () => {
      // Arrange
      const el = React.createElement(MfaForm, { tempToken: 'token.abc' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('Verificar');
    });

    it('should_render_logo_image', () => {
      // Arrange
      const el = React.createElement(MfaForm, { tempToken: 'token.abc' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('src="/next.svg"');
    });

    it('should_render_back_to_login_button', () => {
      // Arrange
      const el = React.createElement(MfaForm, { tempToken: 'tok' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('Volver a login');
    });
  });

  // ---------------------------------------------------------------
  // 2. Negative cases (error handling)
  // ---------------------------------------------------------------
  describe('Negative cases', () => {
    it('should_render_verify_button_disabled_when_code_empty', () => {
      // Arrange — code is empty initially → button disabled
      const el = React.createElement(MfaForm, { tempToken: 'tok' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('disabled');
    });

    it('should_not_crash_when_only_tempToken_provided', () => {
      // Arrange
      const el = React.createElement(MfaForm, { tempToken: '' });

      // Act & Assert
      expect(() => ReactDOMServer.renderToStaticMarkup(el)).to.not.throw();
    });

    it('should_not_crash_when_onBackToLogin_is_undefined', () => {
      // Arrange
      const el = React.createElement(MfaForm, { tempToken: 'tok', onBackToLogin: undefined });

      // Act & Assert
      expect(() => ReactDOMServer.renderToStaticMarkup(el)).to.not.throw();
    });
  });

  // ---------------------------------------------------------------
  // 3. Edge cases
  // ---------------------------------------------------------------
  describe('Edge cases', () => {
    it('should_render_instruction_subtitle', () => {
      // Arrange
      const el = React.createElement(MfaForm, { tempToken: 'tok' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('6 dígitos');
    });

    it('should_render_custom_logo_src', () => {
      // Arrange
      const el = React.createElement(MfaForm, { tempToken: 'tok', logoSrc: '/brand.svg' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('src="/brand.svg"');
    });

    it('should_apply_custom_className_to_section', () => {
      // Arrange
      const el = React.createElement(MfaForm, { tempToken: 'tok', className: 'mfa-custom' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('mfa-custom');
    });
  });

  // ---------------------------------------------------------------
  // 4. Interaction cases
  // ---------------------------------------------------------------
  describe('Interaction cases', () => {
    it('should_have_numeric_otp_inputs', () => {
      // Arrange
      const el = React.createElement(MfaForm, { tempToken: 'tok' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('inputMode="numeric"');
    });

    it('should_have_otp_group_role', () => {
      // Arrange
      const el = React.createElement(MfaForm, { tempToken: 'tok' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('role="group"');
    });

    it('should_have_autocomplete_one_time_code_on_inputs', () => {
      // Arrange
      const el = React.createElement(MfaForm, { tempToken: 'tok' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('autoComplete="one-time-code"');
    });
  });

  // ---------------------------------------------------------------
  // 5. State transition cases
  // ---------------------------------------------------------------
  describe('State transition cases', () => {
    it('should_not_show_verificando_text_in_initial_state', () => {
      // Arrange
      const el = React.createElement(MfaForm, { tempToken: 'tok' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.not.contain('Verificando...');
    });

    it('should_show_verificar_text_in_initial_state', () => {
      // Arrange
      const el = React.createElement(MfaForm, { tempToken: 'tok' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('Verificar');
    });
  });

  // ---------------------------------------------------------------
  // 6. Accessibility cases
  // ---------------------------------------------------------------
  describe('Accessibility cases', () => {
    it('should_have_section_aria_label_mfa', () => {
      // Arrange
      const el = React.createElement(MfaForm, { tempToken: 'tok' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('aria-label="Verificación MFA"');
    });

    it('should_have_form_aria_label_security_verification', () => {
      // Arrange
      const el = React.createElement(MfaForm, { tempToken: 'tok' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('aria-label="Verificación de seguridad"');
    });

    it('should_have_aria_label_on_each_otp_input', () => {
      // Arrange
      const el = React.createElement(MfaForm, { tempToken: 'tok' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      for (let i = 1; i <= 6; i++) {
        expect(html).to.contain(`Dígito ${i} de 6`);
      }
    });

    it('should_have_group_aria_label_on_otp_container', () => {
      // Arrange
      const el = React.createElement(MfaForm, { tempToken: 'tok' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('aria-label="Código OTP de 6 dígitos"');
    });
  });

  // ---------------------------------------------------------------
  // 7. Props variations
  // ---------------------------------------------------------------
  describe('Props variations', () => {
    it('should_render_with_navigateFn_override', () => {
      // Arrange
      const navFn = sinon.stub();
      const el = React.createElement(MfaForm, { tempToken: 'tok', navigateFn: navFn });

      // Act & Assert
      expect(() => ReactDOMServer.renderToStaticMarkup(el)).to.not.throw();
    });

    it('should_render_same_structure_with_empty_vs_non_empty_token', () => {
      // Arrange
      const elEmpty = React.createElement(MfaForm, { tempToken: '' });
      const elFull = React.createElement(MfaForm, { tempToken: 'valid.jwt.token' });

      // Act
      const html1 = ReactDOMServer.renderToStaticMarkup(elEmpty);
      const html2 = ReactDOMServer.renderToStaticMarkup(elFull);

      // Assert — both render the same form structure
      expect(html1).to.contain('Verificación de Seguridad');
      expect(html2).to.contain('Verificación de Seguridad');
    });

    it('should_render_custom_alt_text_for_logo', () => {
      // Arrange
      const el = React.createElement(MfaForm, { tempToken: 'tok', logoAlt: 'Custom Logo' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('alt="Custom Logo"');
    });
  });
});
