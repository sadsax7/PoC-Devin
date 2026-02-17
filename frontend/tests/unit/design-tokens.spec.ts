/**
 * @fileoverview Tests for design-tokens.ts
 *
 * Validates that design tokens match the institutional requirements
 * defined in HU-FE-00 Acceptance Criteria #2.
 *
 * @remarks
 * Pattern: AAA (Arrange-Act-Assert).
 * Naming convention: should_<expected>_when_<condition>.
 */

import { expect } from 'chai';
import {
  colors,
  fonts,
  fontWeights,
  spacing,
  radii,
  designTokens,
} from '../../src/styles/design-tokens';

describe('Design Tokens', () => {
  describe('Colors', () => {
    it('should_have_primary_orange_when_accessed', () => {
      // Arrange & Act
      const primary = colors.primary;

      // Assert
      expect(primary).to.equal('#FF6B00');
    });

    it('should_have_black_bg_dark_when_accessed', () => {
      // Arrange & Act
      const bgDark = colors.bgDark;

      // Assert
      expect(bgDark).to.equal('#000000');
    });

    it('should_have_white_text_light_when_accessed', () => {
      // Arrange & Act
      const textLight = colors.textLight;

      // Assert
      expect(textLight).to.equal('#FFFFFF');
    });

    it('should_have_exactly_three_color_tokens_when_checked', () => {
      // Arrange & Act
      const keys = Object.keys(colors);

      // Assert
      expect(keys).to.have.length(3);
      expect(keys).to.include.members(['primary', 'bgDark', 'textLight']);
    });

    it('should_have_valid_hex_format_when_all_colors_checked', () => {
      // Arrange
      const hexRegex = /^#[0-9A-Fa-f]{6}$/;

      // Act & Assert
      Object.values(colors).forEach((color) => {
        expect(color).to.match(hexRegex, `Color ${color} is not a valid hex`);
      });
    });
  });

  describe('Fonts', () => {
    it('should_have_inter_as_primary_font_when_accessed', () => {
      // Arrange & Act
      const fontFamily = fonts.sans;

      // Assert
      expect(fontFamily).to.include('Inter');
    });

    it('should_have_system_fallbacks_when_inter_unavailable', () => {
      // Arrange & Act
      const fontFamily = fonts.sans;

      // Assert
      expect(fontFamily).to.include('ui-sans-serif');
      expect(fontFamily).to.include('system-ui');
      expect(fontFamily).to.include('sans-serif');
    });
  });

  describe('Font Weights', () => {
    it('should_have_five_weight_levels_when_accessed', () => {
      // Arrange & Act
      const keys = Object.keys(fontWeights);

      // Assert
      expect(keys).to.have.length(5);
    });

    it('should_have_correct_weight_values_when_checked', () => {
      // Assert
      expect(fontWeights.light).to.equal(300);
      expect(fontWeights.regular).to.equal(400);
      expect(fontWeights.medium).to.equal(500);
      expect(fontWeights.semibold).to.equal(600);
      expect(fontWeights.bold).to.equal(700);
    });

    it('should_have_only_numeric_values_when_all_weights_checked', () => {
      // Act & Assert
      Object.values(fontWeights).forEach((weight) => {
        expect(weight).to.be.a('number');
        expect(weight).to.be.greaterThan(0);
      });
    });
  });

  describe('Spacing', () => {
    it('should_have_six_spacing_levels_when_accessed', () => {
      // Arrange & Act
      const keys = Object.keys(spacing);

      // Assert
      expect(keys).to.have.length(6);
    });

    it('should_have_valid_pixel_values_when_checked', () => {
      // Act & Assert
      Object.values(spacing).forEach((value) => {
        expect(value).to.match(/^\d+px$/, `Spacing ${value} is not a valid px value`);
      });
    });
  });

  describe('Radii', () => {
    it('should_have_four_radius_levels_when_accessed', () => {
      // Arrange & Act
      const keys = Object.keys(radii);

      // Assert
      expect(keys).to.have.length(4);
    });

    it('should_include_full_radius_for_circles_when_checked', () => {
      // Assert
      expect(radii.full).to.equal('9999px');
    });
  });

  describe('Default Export', () => {
    it('should_consolidate_all_tokens_when_imported', () => {
      // Assert
      expect(designTokens).to.have.property('colors');
      expect(designTokens).to.have.property('fonts');
      expect(designTokens).to.have.property('fontWeights');
      expect(designTokens).to.have.property('spacing');
      expect(designTokens).to.have.property('radii');
    });
  });
});
