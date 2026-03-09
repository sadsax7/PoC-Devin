/**
 * @fileoverview Tests for the ErrorMessage atom component.
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
import { ErrorMessage } from '../../../src/components/atoms';

describe('ErrorMessage', () => {
  // ---------------------------------------------------------------
  // 1. Positive cases (happy path)
  // ---------------------------------------------------------------
  describe('Positive cases', () => {
    it('should_render_message_text_when_message_provided', () => {
      // Arrange
      const element = React.createElement(ErrorMessage, { message: 'Something went wrong' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('Something went wrong');
    });

    it('should_render_icon_by_default', () => {
      // Arrange
      const element = React.createElement(ErrorMessage, { message: 'Error' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('✕');
    });
  });

  // ---------------------------------------------------------------
  // 2. Negative cases (error handling)
  // ---------------------------------------------------------------
  describe('Negative cases', () => {
    it('should_return_null_when_message_is_undefined', () => {
      // Arrange
      const element = React.createElement(ErrorMessage, {});

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.equal('');
    });

    it('should_return_null_when_message_is_empty_string', () => {
      // Arrange
      const element = React.createElement(ErrorMessage, { message: '' });

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
      const longMsg = 'A'.repeat(300);
      const element = React.createElement(ErrorMessage, { message: longMsg });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain(longMsg);
    });

    it('should_render_message_with_special_characters', () => {
      // Arrange
      const element = React.createElement(ErrorMessage, {
        message: 'Error: <script>alert("xss")</script>',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert — React escapes HTML entities
      expect(html).to.contain('&lt;script&gt;');
      expect(html).to.not.contain('<script>');
    });
  });

  // ---------------------------------------------------------------
  // 4. Interaction cases
  // ---------------------------------------------------------------
  describe('Interaction cases', () => {
    it('should_render_without_icon_when_showIcon_false', () => {
      // Arrange
      const element = React.createElement(ErrorMessage, {
        message: 'Error',
        showIcon: false,
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.not.contain('✕');
      expect(html).to.contain('Error');
    });
  });

  // ---------------------------------------------------------------
  // 5. State transition cases
  // ---------------------------------------------------------------
  describe('State transition cases', () => {
    it('should_render_when_message_transitions_from_empty_to_present', () => {
      // Arrange — simulate "no error" → "error"
      const noError = React.createElement(ErrorMessage, { message: '' });
      const withError = React.createElement(ErrorMessage, { message: 'Oops' });

      // Act
      const htmlEmpty = ReactDOMServer.renderToStaticMarkup(noError);
      const htmlWithError = ReactDOMServer.renderToStaticMarkup(withError);

      // Assert
      expect(htmlEmpty).to.equal('');
      expect(htmlWithError).to.contain('Oops');
    });
  });

  // ---------------------------------------------------------------
  // 6. Accessibility cases
  // ---------------------------------------------------------------
  describe('Accessibility cases', () => {
    it('should_have_role_alert', () => {
      // Arrange
      const element = React.createElement(ErrorMessage, { message: 'Error' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('role="alert"');
    });

    it('should_have_aria_live_polite', () => {
      // Arrange
      const element = React.createElement(ErrorMessage, { message: 'Error' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('aria-live="polite"');
    });

    it('should_mark_icon_as_aria_hidden', () => {
      // Arrange
      const element = React.createElement(ErrorMessage, { message: 'Error' });

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
      const element = React.createElement(ErrorMessage, {
        message: 'Error',
        className: 'my-custom-class',
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('my-custom-class');
    });

    it('should_apply_default_red_text_color', () => {
      // Arrange
      const element = React.createElement(ErrorMessage, { message: 'Error' });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('text-red-500');
    });

    it('should_render_with_showIcon_true_explicitly', () => {
      // Arrange
      const element = React.createElement(ErrorMessage, {
        message: 'Error',
        showIcon: true,
      });

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('✕');
    });
  });
});
