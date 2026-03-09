/**
 * @fileoverview Tests for the SuccessMessage atom component.
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
import { SuccessMessage } from '../../../src/components/atoms';

describe('SuccessMessage', () => {
  // ---------------------------------------------------------------
  // 1. Positive cases (happy path)
  // ---------------------------------------------------------------
  describe('Positive cases', () => {
    it('should_render_message_text_when_message_provided', () => {
      // Arrange
      const element = React.createElement(SuccessMessage, { message: 'Account created!' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('Account created!');
    });

    it('should_render_checkmark_icon_by_default', () => {
      // Arrange
      const element = React.createElement(SuccessMessage, { message: 'OK' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('✓');
    });
  });

  // ---------------------------------------------------------------
  // 2. Negative cases (error handling)
  // ---------------------------------------------------------------
  describe('Negative cases', () => {
    it('should_return_null_when_message_is_undefined', () => {
      // Arrange
      const element = React.createElement(SuccessMessage, {});

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.equal('');
    });

    it('should_return_null_when_message_is_empty_string', () => {
      // Arrange
      const element = React.createElement(SuccessMessage, { message: '' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.equal('');
    });
  });

  // ---------------------------------------------------------------
  // 3. Edge cases
  // ---------------------------------------------------------------
  describe('Edge cases', () => {
    it('should_render_long_messages_without_truncation', () => {
      // Arrange
      const longMsg = 'Success! '.repeat(50);
      const element = React.createElement(SuccessMessage, { message: longMsg });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain(longMsg.trim());
    });

    it('should_escape_html_in_message', () => {
      // Arrange
      const element = React.createElement(SuccessMessage, {
        message: '<b>Bold</b>',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('&lt;b&gt;');
    });
  });

  // ---------------------------------------------------------------
  // 4. Interaction cases
  // ---------------------------------------------------------------
  describe('Interaction cases', () => {
    it('should_render_without_icon_when_showIcon_false', () => {
      // Arrange
      const element = React.createElement(SuccessMessage, {
        message: 'Done',
        showIcon: false,
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.not.contain('✓');
      expect(html).to.contain('Done');
    });
  });

  // ---------------------------------------------------------------
  // 5. State transition cases
  // ---------------------------------------------------------------
  describe('State transition cases', () => {
    it('should_render_when_message_transitions_from_empty_to_present', () => {
      // Arrange
      const noMsg = React.createElement(SuccessMessage, { message: '' });
      const withMsg = React.createElement(SuccessMessage, { message: 'OK' });

      // Act
      const htmlEmpty = ReactDOMServer.renderToStaticMarkup(noMsg);
      const htmlWithMsg = ReactDOMServer.renderToStaticMarkup(withMsg);

      // Assert
      expect(htmlEmpty).to.equal('');
      expect(htmlWithMsg).to.contain('OK');
    });
  });

  // ---------------------------------------------------------------
  // 6. Accessibility cases
  // ---------------------------------------------------------------
  describe('Accessibility cases', () => {
    it('should_have_role_status', () => {
      // Arrange
      const element = React.createElement(SuccessMessage, { message: 'OK' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('role="status"');
    });

    it('should_have_aria_live_polite', () => {
      // Arrange
      const element = React.createElement(SuccessMessage, { message: 'OK' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('aria-live="polite"');
    });

    it('should_mark_icon_as_aria_hidden', () => {
      // Arrange
      const element = React.createElement(SuccessMessage, { message: 'OK' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('aria-hidden="true"');
    });
  });

  // ---------------------------------------------------------------
  // 7. Props variations
  // ---------------------------------------------------------------
  describe('Props variations', () => {
    it('should_apply_custom_className', () => {
      // Arrange
      const element = React.createElement(SuccessMessage, {
        message: 'OK',
        className: 'extra-class',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('extra-class');
    });

    it('should_apply_green_text_color', () => {
      // Arrange
      const element = React.createElement(SuccessMessage, { message: 'OK' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('text-green-500');
    });

    it('should_render_with_showIcon_true_explicitly', () => {
      // Arrange
      const element = React.createElement(SuccessMessage, {
        message: 'OK',
        showIcon: true,
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('✓');
    });
  });
});
