/**
 * @fileoverview Tests for the FormField molecule component.
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
import { FormField } from '../../../src/components/molecules';

describe('FormField', () => {
  // ---------------------------------------------------------------
  // 1. Positive cases (happy path)
  // ---------------------------------------------------------------
  describe('Positive cases', () => {
    it('should_render_label_and_input_when_required_props_provided', () => {
      // Arrange
      const element = React.createElement(FormField, { id: 'phone', label: 'Teléfono' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('Teléfono');
      expect(html).to.contain('<input');
    });

    it('should_render_helper_text_when_no_error', () => {
      // Arrange
      const element = React.createElement(FormField, {
        id: 'phone',
        label: 'Teléfono',
        helperText: 'Formato E.164',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('Formato E.164');
    });

    it('should_render_with_placeholder', () => {
      // Arrange
      const element = React.createElement(FormField, {
        id: 'phone',
        label: 'Teléfono',
        placeholder: 'ej: +573001234567',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('placeholder="ej: +573001234567"');
    });
  });

  // ---------------------------------------------------------------
  // 2. Negative cases (error handling)
  // ---------------------------------------------------------------
  describe('Negative cases', () => {
    it('should_show_error_and_hide_helper_when_error_provided', () => {
      // Arrange
      const element = React.createElement(FormField, {
        id: 'phone',
        label: 'Teléfono',
        error: 'Formato inválido',
        helperText: 'Formato E.164',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('Formato inválido');
      expect(html).to.not.contain('Formato E.164');
    });

    it('should_not_crash_when_no_error_and_no_helper', () => {
      // Arrange
      const element = React.createElement(FormField, {
        id: 'phone',
        label: 'Teléfono',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('<input');
    });
  });

  // ---------------------------------------------------------------
  // 3. Edge cases
  // ---------------------------------------------------------------
  describe('Edge cases', () => {
    it('should_handle_empty_string_error', () => {
      // Arrange
      const element = React.createElement(FormField, {
        id: 'phone',
        label: 'Teléfono',
        error: '',
        helperText: 'Helper visible',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert — empty error is falsy, helper should show
      expect(html).to.contain('Helper visible');
    });

    it('should_handle_undefined_helperText', () => {
      // Arrange
      const element = React.createElement(FormField, {
        id: 'phone',
        label: 'Teléfono',
        helperText: undefined,
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('<input');
    });

    it('should_set_maxLength_on_input', () => {
      // Arrange
      const element = React.createElement(FormField, {
        id: 'name',
        label: 'Nombre',
        maxLength: 100,
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert — React SSR may use camelCase or lowercase for maxLength
      expect(html.toLowerCase()).to.contain('maxlength="100"');
    });
  });

  // ---------------------------------------------------------------
  // 4. Interaction cases
  // ---------------------------------------------------------------
  describe('Interaction cases', () => {
    it('should_pass_suffix_to_TextField', () => {
      // Arrange
      const suffix = React.createElement('span', null, '👁');
      const element = React.createElement(FormField, {
        id: 'password',
        label: 'Contraseña',
        suffix,
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('👁');
    });

    it('should_accept_onChange_handler', () => {
      // Arrange
      const element = React.createElement(FormField, {
        id: 'phone',
        label: 'Teléfono',
        onChange: () => {},
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('<input');
    });
  });

  // ---------------------------------------------------------------
  // 5. State transition cases
  // ---------------------------------------------------------------
  describe('State transition cases', () => {
    it('should_prioritize_error_over_helper_text', () => {
      // Arrange — simulate error appearing
      const withHelper = React.createElement(FormField, {
        id: 'phone',
        label: 'Teléfono',
        helperText: 'Helper',
      });
      const withError = React.createElement(FormField, {
        id: 'phone',
        label: 'Teléfono',
        error: 'Error!',
        helperText: 'Helper',
      });

      // Act
      const htmlHelper = ReactDOMServer.renderToStaticMarkup(withHelper);
      const htmlError = ReactDOMServer.renderToStaticMarkup(withError);

      // Assert
      expect(htmlHelper).to.contain('Helper');
      expect(htmlError).to.contain('Error!');
      expect(htmlError).to.not.contain('Helper');
    });

    it('should_show_disabled_state_when_disabled', () => {
      // Arrange
      const element = React.createElement(FormField, {
        id: 'phone',
        label: 'Teléfono',
        disabled: true,
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('disabled');
    });
  });

  // ---------------------------------------------------------------
  // 6. Accessibility cases
  // ---------------------------------------------------------------
  describe('Accessibility cases', () => {
    it('should_link_helper_via_aria_describedby_when_no_error', () => {
      // Arrange
      const element = React.createElement(FormField, {
        id: 'phone',
        label: 'Teléfono',
        helperText: 'Help',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('aria-describedby="phone-helper"');
      expect(html).to.contain('id="phone-helper"');
    });

    it('should_link_error_via_aria_describedby_when_error_present', () => {
      // Arrange
      const element = React.createElement(FormField, {
        id: 'phone',
        label: 'Teléfono',
        error: 'Bad',
        helperText: 'Help',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('aria-describedby="phone-error"');
    });

    it('should_have_label_linked_to_input', () => {
      // Arrange
      const element = React.createElement(FormField, {
        id: 'email',
        label: 'Email',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('for="email"');
      expect(html).to.contain('id="email"');
    });
  });

  // ---------------------------------------------------------------
  // 7. Props variations
  // ---------------------------------------------------------------
  describe('Props variations', () => {
    it('should_render_password_type', () => {
      // Arrange
      const element = React.createElement(FormField, {
        id: 'pass',
        label: 'Password',
        type: 'password',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('type="password"');
    });

    it('should_render_email_type', () => {
      // Arrange
      const element = React.createElement(FormField, {
        id: 'email',
        label: 'Email',
        type: 'email',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('type="email"');
    });

    it('should_apply_custom_className', () => {
      // Arrange
      const element = React.createElement(FormField, {
        id: 'test',
        label: 'Test',
        className: 'custom-wrapper',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('custom-wrapper');
    });

    it('should_render_with_value_prop', () => {
      // Arrange
      const element = React.createElement(FormField, {
        id: 'phone',
        label: 'Phone',
        value: '+573001234567',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('value="+573001234567"');
    });
  });
});
