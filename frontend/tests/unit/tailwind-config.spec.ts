/**
 * @fileoverview Tests for tailwind.config.js
 *
 * Validates that Tailwind config matches HU-FE-00 requirements:
 * correct tokens, dark mode strategy, and Inter font.
 *
 * @remarks
 * Pattern: AAA (Arrange-Act-Assert).
 */

import { expect } from 'chai';
// eslint-disable-next-line @typescript-eslint/no-require-imports
const tailwindConfig = require('../../tailwind.config.js');

describe('Tailwind Config', () => {
  describe('Dark Mode', () => {
    it('should_use_class_strategy_when_checked', () => {
      // Assert
      expect(tailwindConfig.darkMode).to.equal('class');
    });
  });

  describe('Colors', () => {
    it('should_have_primary_orange_when_accessed', () => {
      // Arrange
      const colors = tailwindConfig.theme.extend.colors;

      // Assert
      expect(colors.primary).to.equal('#FF6B00');
    });

    it('should_have_bg_dark_black_when_accessed', () => {
      // Arrange
      const colors = tailwindConfig.theme.extend.colors;

      // Assert
      expect(colors['bg-dark']).to.equal('#000000');
    });

    it('should_have_text_light_white_when_accessed', () => {
      // Arrange
      const colors = tailwindConfig.theme.extend.colors;

      // Assert
      expect(colors['text-light']).to.equal('#FFFFFF');
    });
  });

  describe('Font Family', () => {
    it('should_have_inter_as_first_font_when_checked', () => {
      // Arrange
      const fontFamily = tailwindConfig.theme.extend.fontFamily;

      // Assert
      expect(fontFamily.sans[0]).to.equal('Inter');
    });

    it('should_have_system_fallbacks_when_inter_unavailable', () => {
      // Arrange
      const fontFamily = tailwindConfig.theme.extend.fontFamily.sans;

      // Assert
      expect(fontFamily).to.include('ui-sans-serif');
      expect(fontFamily).to.include('system-ui');
    });
  });

  describe('Content paths', () => {
    it('should_include_all_source_directories_when_checked', () => {
      // Arrange
      const content = tailwindConfig.content;

      // Assert
      expect(content).to.be.an('array');
      expect(content.some((p: string) => p.includes('app'))).to.be.true;
      expect(content.some((p: string) => p.includes('components'))).to.be.true;
    });
  });
});
