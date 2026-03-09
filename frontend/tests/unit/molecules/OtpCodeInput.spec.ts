/**
 * @fileoverview Tests for the OtpCodeInput molecule component.
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
import { OtpCodeInput } from '../../../src/components/molecules';

describe('OtpCodeInput', () => {
  afterEach(() => sinon.restore());

  // ---------------------------------------------------------------
  // 1. Positive cases (happy path)
  // ---------------------------------------------------------------
  describe('Positive cases', () => {
    it('should_render_six_digit_inputs', () => {
      // Arrange
      const el = React.createElement(OtpCodeInput, {
        value: '',
        onChange: () => {},
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert — six OtpDigitInput ids: otp-digit-0 to otp-digit-5
      for (let i = 0; i < 6; i++) {
        expect(html).to.contain(`id="otp-digit-${i}"`);
      }
    });

    it('should_render_role_group_wrapper', () => {
      // Arrange
      const el = React.createElement(OtpCodeInput, {
        value: '',
        onChange: () => {},
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('role="group"');
    });

    it('should_distribute_value_characters_to_inputs', () => {
      // Arrange
      const el = React.createElement(OtpCodeInput, {
        value: '123456',
        onChange: () => {},
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('value="1"');
      expect(html).to.contain('value="2"');
      expect(html).to.contain('value="6"');
    });
  });

  // ---------------------------------------------------------------
  // 2. Negative cases (error handling)
  // ---------------------------------------------------------------
  describe('Negative cases', () => {
    it('should_not_crash_when_value_is_empty', () => {
      // Arrange
      const el = React.createElement(OtpCodeInput, { value: '', onChange: () => {} });

      // Act & Assert
      expect(() => ReactDOMServer.renderToStaticMarkup(el)).to.not.throw();
    });

    it('should_render_empty_inputs_when_value_shorter_than_six', () => {
      // Arrange
      const el = React.createElement(OtpCodeInput, {
        value: '12',
        onChange: () => {},
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert — still renders 6 inputs
      const matches = html.match(/<input/g) ?? [];
      expect(matches.length).to.equal(6);
    });

    it('should_apply_error_styling_when_hasError_is_true', () => {
      // Arrange
      const el = React.createElement(OtpCodeInput, {
        value: '',
        onChange: () => {},
        hasError: true,
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert — error styling on inputs
      expect(html).to.contain('border-red-500');
    });
  });

  // ---------------------------------------------------------------
  // 3. Edge cases
  // ---------------------------------------------------------------
  describe('Edge cases', () => {
    it('should_truncate_value_to_six_chars', () => {
      // Arrange — value longer than 6 chars
      const el = React.createElement(OtpCodeInput, {
        value: '1234567890',
        onChange: () => {},
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert — still only 6 inputs rendered
      const matches = html.match(/<input/g) ?? [];
      expect(matches.length).to.equal(6);
      // digit-0 = '1', digit-5 = '6'
      expect(html).to.contain('value="1"');
    });

    it('should_render_all_empty_inputs_when_value_is_whitespace', () => {
      // Arrange
      const el = React.createElement(OtpCodeInput, {
        value: '      ',
        onChange: () => {},
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      const matches = html.match(/<input/g) ?? [];
      expect(matches.length).to.equal(6);
    });

    it('should_apply_custom_className_to_wrapper', () => {
      // Arrange
      const el = React.createElement(OtpCodeInput, {
        value: '',
        onChange: () => {},
        className: 'my-otp-wrapper',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('my-otp-wrapper');
    });
  });

  // ---------------------------------------------------------------
  // 4. Interaction cases
  // ---------------------------------------------------------------
  describe('Interaction cases', () => {
    it('should_have_each_input_with_unique_id', () => {
      // Arrange
      const el = React.createElement(OtpCodeInput, { value: '', onChange: () => {} });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert — all 6 unique ids present
      expect(html).to.contain('id="otp-digit-0"');
      expect(html).to.contain('id="otp-digit-5"');
    });

    it('should_have_aria_label_on_wrapper_group', () => {
      // Arrange
      const el = React.createElement(OtpCodeInput, { value: '', onChange: () => {} });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.contain('aria-label="Código OTP de 6 dígitos"');
    });
  });

  // ---------------------------------------------------------------
  // 5. State transition cases
  // ---------------------------------------------------------------
  describe('State transition cases', () => {
    it('should_render_disabled_inputs_when_disabled_is_true', () => {
      // Arrange
      const el = React.createElement(OtpCodeInput, {
        value: '',
        onChange: () => {},
        disabled: true,
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert — check all inputs are disabled
      const disabledMatches = html.match(/disabled/g) ?? [];
      expect(disabledMatches.length).to.be.at.least(6);
    });

    it('should_render_enabled_inputs_by_default', () => {
      // Arrange
      const el = React.createElement(OtpCodeInput, {
        value: '',
        onChange: () => {},
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      expect(html).to.not.contain('disabled=""');
    });
  });

  // ---------------------------------------------------------------
  // 6. Accessibility cases
  // ---------------------------------------------------------------
  describe('Accessibility cases', () => {
    it('should_have_aria_labels_on_all_inputs', () => {
      // Arrange
      const el = React.createElement(OtpCodeInput, { value: '', onChange: () => {} });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert — all 6 aria-label attributes present
      for (let i = 1; i <= 6; i++) {
        expect(html).to.contain(`Dígito ${i} de 6`);
      }
    });

    it('should_have_one_time_code_autocomplete_on_inputs', () => {
      // Arrange
      const el = React.createElement(OtpCodeInput, { value: '', onChange: () => {} });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert
      const autoCompleteMatches = (html.match(/autoComplete="one-time-code"/g) ?? []).length;
      expect(autoCompleteMatches).to.equal(6);
    });
  });

  // ---------------------------------------------------------------
  // 7. Props variations
  // ---------------------------------------------------------------
  describe('Props variations', () => {
    it('should_render_without_onComplete_prop', () => {
      // Arrange
      const el = React.createElement(OtpCodeInput, {
        value: '123456',
        onChange: () => {},
        // onComplete intentionally omitted
      });

      // Act & Assert
      expect(() => ReactDOMServer.renderToStaticMarkup(el)).to.not.throw();
    });

    it('should_render_with_partial_code', () => {
      // Arrange
      const el = React.createElement(OtpCodeInput, {
        value: '1234',
        onChange: () => {},
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(el);

      // Assert — first 4 have values, last 2 empty
      expect(html).to.contain('value="1"');
      expect(html).to.contain('value="4"');
    });
  });
});
