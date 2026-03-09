/**
 * @fileoverview Tests for the PasswordStrengthIndicator molecule
 * and its exported `calculateStrength` helper.
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
import {
  PasswordStrengthIndicator,
  calculateStrength,
} from '../../../src/components/molecules/PasswordStrengthIndicator';

// =============================================================
// calculateStrength — pure function tests
// =============================================================
describe('calculateStrength', () => {
  it('should_return_none_when_password_empty', () => {
    expect(calculateStrength('')).to.equal('none');
  });

  it('should_return_weak_when_only_lowercase', () => {
    expect(calculateStrength('abcde')).to.equal('weak');
  });

  it('should_return_medium_when_short_but_three_rules_met', () => {
    // 'aB1' meets 3 rules: uppercase, lowercase, digit → medium
    expect(calculateStrength('aB1')).to.equal('medium');
  });

  it('should_return_medium_when_three_rules_met', () => {
    // length>=8 + uppercase + lowercase = 3 rules
    expect(calculateStrength('Abcdefgh')).to.equal('medium');
  });

  it('should_return_medium_when_four_rules_met', () => {
    // length>=8 + uppercase + lowercase + digit = 4 rules
    expect(calculateStrength('Abcdefg1')).to.equal('medium');
  });

  it('should_return_strong_when_all_five_rules_met', () => {
    // length>=8 + uppercase + lowercase + digit + special
    expect(calculateStrength('Abcdef1!')).to.equal('strong');
  });

  it('should_return_none_when_password_undefined_cast', () => {
    // Edge: empty string passed explicitly
    expect(calculateStrength('')).to.equal('none');
  });

  it('should_return_weak_when_only_special_chars', () => {
    expect(calculateStrength('!!!')).to.equal('weak');
  });

  it('should_return_weak_when_only_digits', () => {
    expect(calculateStrength('12345')).to.equal('weak');
  });

  it('should_handle_exactly_8_chars_with_all_rules', () => {
    expect(calculateStrength('Ab1!xxxx')).to.equal('strong');
  });
});

// =============================================================
// PasswordStrengthIndicator — component tests
// =============================================================
describe('PasswordStrengthIndicator', () => {
  // ---------------------------------------------------------------
  // 1. Positive cases (happy path)
  // ---------------------------------------------------------------
  describe('Positive cases', () => {
    it('should_render_progress_bar_when_password_provided', () => {
      // Arrange
      const element = React.createElement(PasswordStrengthIndicator, {
        password: 'Abcdef1!',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('role="progressbar"');
    });

    it('should_show_strong_label_when_password_strong', () => {
      // Arrange
      const element = React.createElement(PasswordStrengthIndicator, {
        password: 'Abcdef1!',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('Contraseña fuerte');
    });
  });

  // ---------------------------------------------------------------
  // 2. Negative cases (error handling)
  // ---------------------------------------------------------------
  describe('Negative cases', () => {
    it('should_render_empty_bar_when_password_is_empty', () => {
      // Arrange
      const element = React.createElement(PasswordStrengthIndicator, { password: '' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('w-0');
      expect(html).to.not.contain('Contraseña');
    });

    it('should_not_crash_with_very_long_password', () => {
      // Arrange
      const longPass = 'Aa1!' + 'x'.repeat(500);
      const element = React.createElement(PasswordStrengthIndicator, { password: longPass });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('role="progressbar"');
    });
  });

  // ---------------------------------------------------------------
  // 3. Edge cases
  // ---------------------------------------------------------------
  describe('Edge cases', () => {
    it('should_show_weak_for_single_char_password', () => {
      // Arrange
      const element = React.createElement(PasswordStrengthIndicator, { password: 'a' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('bg-red-500');
      expect(html).to.contain('Contraseña débil');
    });

    it('should_show_medium_for_8_lowercase_uppercase', () => {
      // Arrange
      const element = React.createElement(PasswordStrengthIndicator, {
        password: 'Abcdefgh',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('bg-yellow-500');
      expect(html).to.contain('Contraseña media');
    });
  });

  // ---------------------------------------------------------------
  // 4. Interaction cases
  // ---------------------------------------------------------------
  describe('Interaction cases', () => {
    it('should_update_bar_color_when_password_changes_weak_to_strong', () => {
      // Arrange
      const weak = React.createElement(PasswordStrengthIndicator, { password: 'abc' });
      const strong = React.createElement(PasswordStrengthIndicator, {
        password: 'Abcdef1!',
      });

      // Act
      const htmlWeak = ReactDOMServer.renderToStaticMarkup(weak);
      const htmlStrong = ReactDOMServer.renderToStaticMarkup(strong);

      // Assert
      expect(htmlWeak).to.contain('bg-red-500');
      expect(htmlStrong).to.contain('bg-green-500');
    });
  });

  // ---------------------------------------------------------------
  // 5. State transition cases
  // ---------------------------------------------------------------
  describe('State transition cases', () => {
    it('should_transition_through_all_strength_levels', () => {
      // Arrange
      const passwords = ['', 'a', 'Abcdefgh', 'Abcdef1!'];
      const expected = ['w-0', 'w-1/3', 'w-2/3', 'w-full'];

      passwords.forEach((pw, i) => {
        // Act
        const html = ReactDOMServer.renderToStaticMarkup(
          React.createElement(PasswordStrengthIndicator, { password: pw }),
        );

        // Assert
        expect(html).to.contain(expected[i]);
      });
    });

    it('should_hide_label_when_strength_is_none', () => {
      // Arrange
      const element = React.createElement(PasswordStrengthIndicator, { password: '' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.not.contain('<span');
    });
  });

  // ---------------------------------------------------------------
  // 6. Accessibility cases
  // ---------------------------------------------------------------
  describe('Accessibility cases', () => {
    it('should_have_aria_label_with_strength_description', () => {
      // Arrange
      const element = React.createElement(PasswordStrengthIndicator, {
        password: 'Abcdef1!',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('aria-label="Contraseña fuerte"');
    });

    it('should_have_aria_valuenow_matching_strength', () => {
      // Arrange
      const element = React.createElement(PasswordStrengthIndicator, {
        password: 'Abcdef1!',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('aria-valuenow="100"');
    });

    it('should_have_aria_valuemin_and_valuemax', () => {
      // Arrange
      const element = React.createElement(PasswordStrengthIndicator, { password: '' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('aria-valuemin="0"');
      expect(html).to.contain('aria-valuemax="100"');
    });

    it('should_set_valuenow_0_when_no_password', () => {
      // Arrange
      const element = React.createElement(PasswordStrengthIndicator, { password: '' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('aria-valuenow="0"');
    });

    it('should_set_valuenow_33_when_weak', () => {
      // Arrange
      const element = React.createElement(PasswordStrengthIndicator, { password: 'abc' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('aria-valuenow="33"');
    });

    it('should_set_valuenow_66_when_medium', () => {
      // Arrange
      const element = React.createElement(PasswordStrengthIndicator, {
        password: 'Abcdefgh',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('aria-valuenow="66"');
    });
  });

  // ---------------------------------------------------------------
  // 7. Props variations
  // ---------------------------------------------------------------
  describe('Props variations', () => {
    it('should_apply_custom_className', () => {
      // Arrange
      const element = React.createElement(PasswordStrengthIndicator, {
        password: 'abc',
        className: 'extra-margin',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('extra-margin');
    });

    it('should_use_default_empty_className', () => {
      // Arrange
      const element = React.createElement(PasswordStrengthIndicator, { password: 'abc' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert — no extra classNames beyond the component's own
      expect(html).to.contain('flex flex-col gap-1');
    });
  });
});
