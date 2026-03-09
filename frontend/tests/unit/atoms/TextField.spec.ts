/**
 * @fileoverview Tests for the TextField atom component.
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
import { TextField } from '../../../src/components/atoms';

describe('TextField', () => {
  // ---------------------------------------------------------------
  // 1. Positive cases (happy path)
  // ---------------------------------------------------------------
  describe('Positive cases', () => {
    it('should_render_input_with_label_when_required_props_provided', () => {
      // Arrange
      const element = React.createElement(TextField, { id: 'phone', label: 'Teléfono' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('<input');
      expect(html).to.contain('id="phone"');
      expect(html).to.contain('Teléfono');
    });

    it('should_render_placeholder_when_provided', () => {
      // Arrange
      const element = React.createElement(TextField, {
        id: 'phone',
        label: 'Teléfono',
        placeholder: 'ej: +573001234567',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('placeholder="ej: +573001234567"');
    });

    it('should_render_with_value_when_controlled', () => {
      // Arrange
      const element = React.createElement(TextField, {
        id: 'phone',
        label: 'Teléfono',
        value: '+573001234567',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('value="+573001234567"');
    });

    it('should_render_label_linked_to_input_via_htmlFor', () => {
      // Arrange
      const element = React.createElement(TextField, { id: 'email', label: 'Email' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('for="email"');
      expect(html).to.contain('id="email"');
    });
  });

  // ---------------------------------------------------------------
  // 2. Negative cases (error handling)
  // ---------------------------------------------------------------
  describe('Negative cases', () => {
    it('should_show_error_message_when_error_prop_provided', () => {
      // Arrange
      const element = React.createElement(TextField, {
        id: 'phone',
        label: 'Teléfono',
        error: 'Formato inválido',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('Formato inválido');
      expect(html).to.contain('role="alert"');
    });

    it('should_not_render_error_when_error_is_empty_string', () => {
      // Arrange
      const element = React.createElement(TextField, {
        id: 'phone',
        label: 'Teléfono',
        error: '',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.not.contain('role="alert"');
    });

    it('should_not_crash_when_onChange_is_undefined', () => {
      // Arrange
      const element = React.createElement(TextField, {
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
    it('should_handle_undefined_value_gracefully', () => {
      // Arrange
      const element = React.createElement(TextField, {
        id: 'phone',
        label: 'Teléfono',
        value: undefined,
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('<input');
    });

    it('should_handle_empty_string_label', () => {
      // Arrange
      const element = React.createElement(TextField, { id: 'test', label: '' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('<label');
    });

    it('should_set_maxLength_attribute_when_provided', () => {
      // Arrange
      const element = React.createElement(TextField, {
        id: 'name',
        label: 'Nombre',
        maxLength: 100,
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert — React SSR may use camelCase or lowercase for maxLength
      expect(html.toLowerCase()).to.contain('maxlength="100"');
    });

    it('should_handle_empty_className', () => {
      // Arrange
      const element = React.createElement(TextField, {
        id: 'test',
        label: 'Test',
        className: '',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('<input');
    });
  });

  // ---------------------------------------------------------------
  // 4. Interaction cases
  // ---------------------------------------------------------------
  describe('Interaction cases', () => {
    it('should_accept_onChange_handler', () => {
      // Arrange — SSR doesn't invoke handlers but accepts them
      const element = React.createElement(TextField, {
        id: 'phone',
        label: 'Teléfono',
        onChange: () => {},
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('<input');
    });

    it('should_render_suffix_element_when_provided', () => {
      // Arrange
      const suffix = React.createElement('span', null, '👁');
      const element = React.createElement(TextField, {
        id: 'password',
        label: 'Contraseña',
        suffix,
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('👁');
    });
  });

  // ---------------------------------------------------------------
  // 5. State transition cases
  // ---------------------------------------------------------------
  describe('State transition cases', () => {
    it('should_show_red_border_when_error_present', () => {
      // Arrange
      const element = React.createElement(TextField, {
        id: 'phone',
        label: 'Teléfono',
        error: 'Invalid',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('border-red-500');
    });

    it('should_show_normal_border_when_no_error', () => {
      // Arrange
      const element = React.createElement(TextField, {
        id: 'phone',
        label: 'Teléfono',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('border-white/20');
      expect(html).to.not.contain('border-red-500');
    });

    it('should_show_disabled_styles_when_disabled', () => {
      // Arrange
      const element = React.createElement(TextField, {
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
    it('should_set_aria_invalid_true_when_error_present', () => {
      // Arrange
      const element = React.createElement(TextField, {
        id: 'phone',
        label: 'Teléfono',
        error: 'Bad format',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('aria-invalid="true"');
    });

    it('should_set_aria_invalid_false_when_no_error', () => {
      // Arrange
      const element = React.createElement(TextField, {
        id: 'phone',
        label: 'Teléfono',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('aria-invalid="false"');
    });

    it('should_link_error_to_input_via_aria_describedby', () => {
      // Arrange
      const element = React.createElement(TextField, {
        id: 'phone',
        label: 'Teléfono',
        error: 'Invalid',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('aria-describedby="phone-error"');
      expect(html).to.contain('id="phone-error"');
    });

    it('should_use_custom_ariaDescribedBy_when_no_error', () => {
      // Arrange
      const element = React.createElement(TextField, {
        id: 'phone',
        label: 'Teléfono',
        ariaDescribedBy: 'phone-helper',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('aria-describedby="phone-helper"');
    });

    it('should_have_error_with_role_alert_and_aria_live', () => {
      // Arrange
      const element = React.createElement(TextField, {
        id: 'phone',
        label: 'Teléfono',
        error: 'Error',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('role="alert"');
      expect(html).to.contain('aria-live="polite"');
    });
  });

  // ---------------------------------------------------------------
  // 7. Props variations
  // ---------------------------------------------------------------
  describe('Props variations', () => {
    it('should_render_text_type_by_default', () => {
      // Arrange
      const element = React.createElement(TextField, {
        id: 'test',
        label: 'Test',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('type="text"');
    });

    it('should_render_password_type_when_specified', () => {
      // Arrange
      const element = React.createElement(TextField, {
        id: 'pass',
        label: 'Password',
        type: 'password',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('type="password"');
    });

    it('should_render_email_type_when_specified', () => {
      // Arrange
      const element = React.createElement(TextField, {
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
      const element = React.createElement(TextField, {
        id: 'test',
        label: 'Test',
        className: 'custom-class',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('custom-class');
    });

    it('should_set_name_attribute_same_as_id', () => {
      // Arrange
      const element = React.createElement(TextField, {
        id: 'phone',
        label: 'Teléfono',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('name="phone"');
    });
  });
});
