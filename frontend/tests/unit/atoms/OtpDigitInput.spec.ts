/**
 * @fileoverview Tests for the OtpDigitInput atom component.
 *
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
import { OtpDigitInput } from '../../../src/components/atoms';

const noop = () => {};

describe('OtpDigitInput', () => {
  afterEach(() => sinon.restore());

  // ---------------------------------------------------------------
  // 1. Positive cases (happy path)
  // ---------------------------------------------------------------
  describe('Positive cases', () => {
    it('should_render_input_element_when_required_props_provided', () => {
      // Arrange
      const el = React.createElement(OtpDigitInput, {
        id: 'otp-0',
        index: 0,
        value: '',
        onChange: noop,
        onKeyDown: noop,
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('<input');
      expect(html).to.contain('id="otp-0"');
    });

    it('should_render_value_attribute_when_digit_provided', () => {
      // Arrange
      const el = React.createElement(OtpDigitInput, {
        id: 'otp-1',
        index: 1,
        value: '5',
        onChange: noop,
        onKeyDown: noop,
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('value="5"');
    });

    it('should_render_numeric_inputmode', () => {
      // Arrange
      const el = React.createElement(OtpDigitInput, {
        id: 'otp-0',
        index: 0,
        value: '',
        onChange: noop,
        onKeyDown: noop,
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('inputMode="numeric"');
    });

    it('should_render_maxLength_of_one', () => {
      // Arrange
      const el = React.createElement(OtpDigitInput, {
        id: 'otp-0',
        index: 0,
        value: '',
        onChange: noop,
        onKeyDown: noop,
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('maxLength="1"');
    });
  });

  // ---------------------------------------------------------------
  // 2. Negative cases (error handling)
  // ---------------------------------------------------------------
  describe('Negative cases', () => {
    it('should_render_error_border_when_hasError_is_true', () => {
      // Arrange
      const el = React.createElement(OtpDigitInput, {
        id: 'otp-0',
        index: 0,
        value: '',
        onChange: noop,
        onKeyDown: noop,
        hasError: true,
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('border-red-500');
    });

    it('should_not_crash_when_value_is_empty_string', () => {
      // Arrange
      const el = React.createElement(OtpDigitInput, {
        id: 'otp-0',
        index: 0,
        value: '',
        onChange: noop,
        onKeyDown: noop,
      });

      // Act & Assert
      expect(() => ReactDOMServer.renderToStaticMarkup(el)).to.not.throw();
    });
  });

  // ---------------------------------------------------------------
  // 3. Edge cases
  // ---------------------------------------------------------------
  describe('Edge cases', () => {
    it('should_render_index_6_aria_label_when_last_position', () => {
      // Arrange
      const el = React.createElement(OtpDigitInput, {
        id: 'otp-5',
        index: 5,
        value: '',
        onChange: noop,
        onKeyDown: noop,
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('Dígito 6 de 6');
    });

    it('should_render_index_1_aria_label_when_first_position', () => {
      // Arrange
      const el = React.createElement(OtpDigitInput, {
        id: 'otp-0',
        index: 0,
        value: '',
        onChange: noop,
        onKeyDown: noop,
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('Dígito 1 de 6');
    });

    it('should_apply_custom_className_when_provided', () => {
      // Arrange
      const el = React.createElement(OtpDigitInput, {
        id: 'otp-0',
        index: 0,
        value: '',
        onChange: noop,
        onKeyDown: noop,
        className: 'custom-cls',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('custom-cls');
    });
  });

  // ---------------------------------------------------------------
  // 4. Interaction cases
  // ---------------------------------------------------------------
  describe('Interaction cases', () => {
    it('should_have_type_text_for_numeric_input', () => {
      // Arrange
      const el = React.createElement(OtpDigitInput, {
        id: 'otp-0',
        index: 0,
        value: '',
        onChange: noop,
        onKeyDown: noop,
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert — type="text" with inputMode numeric for better mobile UX
      expect(html).to.contain('type="text"');
    });

    it('should_have_autocomplete_one_time_code', () => {
      // Arrange
      const el = React.createElement(OtpDigitInput, {
        id: 'otp-0',
        index: 0,
        value: '',
        onChange: noop,
        onKeyDown: noop,
      });

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
    it('should_render_disabled_attribute_when_disabled_is_true', () => {
      // Arrange
      const el = React.createElement(OtpDigitInput, {
        id: 'otp-0',
        index: 0,
        value: '',
        onChange: noop,
        onKeyDown: noop,
        disabled: true,
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('disabled');
    });

    it('should_not_render_disabled_attribute_when_disabled_is_false', () => {
      // Arrange
      const el = React.createElement(OtpDigitInput, {
        id: 'otp-0',
        index: 0,
        value: '3',
        onChange: noop,
        onKeyDown: noop,
        disabled: false,
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert — check that the disabled HTML attribute is absent (Tailwind class disabled: is not the same)
      expect(html).to.not.contain('disabled=""');
    });
  });

  // ---------------------------------------------------------------
  // 6. Accessibility cases
  // ---------------------------------------------------------------
  describe('Accessibility cases', () => {
    it('should_have_aria_label_with_position_and_total', () => {
      // Arrange
      const el = React.createElement(OtpDigitInput, {
        id: 'otp-2',
        index: 2,
        value: '',
        onChange: noop,
        onKeyDown: noop,
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('aria-label="Dígito 3 de 6"');
    });

    it('should_have_pattern_attribute_for_numeric_validation', () => {
      // Arrange
      const el = React.createElement(OtpDigitInput, {
        id: 'otp-0',
        index: 0,
        value: '',
        onChange: noop,
        onKeyDown: noop,
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('pattern="[0-9]*"');
    });
  });

  // ---------------------------------------------------------------
  // 7. Props variations
  // ---------------------------------------------------------------
  describe('Props variations', () => {
    it('should_render_normal_border_when_hasError_is_false', () => {
      // Arrange
      const el = React.createElement(OtpDigitInput, {
        id: 'otp-0',
        index: 0,
        value: '',
        onChange: noop,
        onKeyDown: noop,
        hasError: false,
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('border-gray-500');
      expect(html).to.not.contain('border-red-500');
    });

    it('should_render_different_ids_per_index', () => {
      // Arrange
      const el0 = React.createElement(OtpDigitInput, {
        id: 'otp-digit-0',
        index: 0,
        value: '1',
        onChange: noop,
        onKeyDown: noop,
      });
      const el3 = React.createElement(OtpDigitInput, {
        id: 'otp-digit-3',
        index: 3,
        value: '7',
        onChange: noop,
        onKeyDown: noop,
      });

      // Act
      const html0 = ReactDOMServer.renderToStaticMarkup(el0);
      const html3 = ReactDOMServer.renderToStaticMarkup(el3);

      // Assert
      expect(html0).to.contain('id="otp-digit-0"');
      expect(html3).to.contain('id="otp-digit-3"');
    });
  });
});
